import re
import json
from json import dumps
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import auth, messages
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Empresa, Log, Alerta, Agenda, Feriado, Issue, Issuefile, Settings
from .forms import EmpresaForm, UserForm, GroupForm, AgendaForm, FeriadoForm, IssueForm, SettingsForm
from .extras import clean_request
from .console import Run
from datetime import datetime, date
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.conf import settings
from django.db.models import Q
from .validators import validate_file_extension


@login_required
def index(request):
    if request.user.profile.force_password_change == True:
        messages.warning(request,'<b>Atenção.</b> É necessário trocar sua senha')
        return redirect('change_password')
    return render(request,'core/index.html')

@login_required
@permission_required('core.view_empresa')
def empresas(request):
    empresas = Empresa.objects.all().order_by('nome')
    if request.method == 'POST':
        empresas = empresas.filter(nome__contains=request.POST['pesquisa'])
    return render(request,'core/empresas.html',{'empresas':empresas})

@login_required
@permission_required('auth.view_group')
def grupos(request):
    grupos = Group.objects.all().order_by('name')
    pesquisa = request.GET.get('pesquisa', None)
    if pesquisa:
        grupos = grupos.filter(name__contains=pesquisa)
    if request.GET.get('_associacoes', None):
        grupos = grupos.filter(user=None)
    return render(request,'core/grupos.html',{'grupos':grupos})

@login_required
@permission_required('auth.view_group')
def usuarios_grupo(request, id):
    grupo = Group.objects.get(pk=id)
    usuarios = User.objects.filter(groups=grupo)
    print(usuarios)
    return render(request, 'core/usuarios_grupo.html',{'grupo':grupo,'usuarios':usuarios})


@login_required
@permission_required('auth.view_user')
def usuarios(request):
    usuarios = User.objects.all().order_by('username')
    if request.GET:
        if request.GET.get('pesquisa'):
            usuarios = usuarios.filter(username__contains=request.GET.get('pesquisa'))
        fields = ['email','is_superuser','is_staff','is_active','last_login','last_login__lte']
        try:
            params = clean_request(request.GET, fields)
            usuarios = usuarios.filter(**params)
        except:
            messages.warning(request,'<b class="text-danger">Erro</b> ao filtrar usuário..')
            return redirect('core_usuarios')
    return render(request,'core/usuarios.html',{'usuarios':usuarios})

@login_required
@permission_required('core.view_log')
def logs(request):
    target_model = request.GET.get('target_model',None)
    mensagem = request.GET.get('mensagem',None)
    related = request.GET.get('related',None)
    logs = Log.objects.filter(modelo=target_model,mensagem=mensagem)
    if related:
        logs = logs.filter(objeto_related=related)
    return render(request,'core/logs.html',{'logs':logs})

@login_required
@permission_required('core.docs')
def docs(request, page='core'):
    return render(request,f'core/docs/{page}.html')

@login_required
@permission_required('core.view_agenda')
def agendas(request):
    return render(request,'core/agendas.html')

@login_required
@permission_required('core.view_feriado')
def feriados(request):
    ano = request.POST['ano'] if request.method == 'POST' else date.today().year
    feriados = Feriado.objects.filter(data__year=ano).order_by('data')
    return render(request,'core/feriados.html',{'feriados':feriados,'ano':ano})


@login_required
@permission_required('core.view_issue')
def issues(request):
    if not request.user.has_perm('core.eh_suporte'):
        issues = Issue.objects.filter(followers=request.user).order_by('entrada')
        if request.method == 'POST' and len(request.POST['pesquisa']) > 2:
            issues = issues.filter(assunto__contains=request.POST['pesquisa'])
        else:
            issues = issues.exclude(status='F')
        if not issues:
            messages.warning(request,'Nenhum issue localizado')
        args = {"issues":issues}
    elif request.method == 'POST' and len(request.POST['pesquisa']) > 2:
        issues = Issue.objects.filter(assunto__contains=request.POST['pesquisa']).order_by('entrada')
        if not issues:
            messages.warning(request,'Nenhum issue localizado com o filtro informado')
        args = {"issues":issues}
    else:
        args = {
            "em_espera": Issue.objects.filter(status='E').order_by('entrada') if request.user.has_perm('core.eh_suporte') else Issue.objects.filter(status='E',followers=request.user).order_by('entrada'),
            "em_atendimento": Issue.objects.filter(status__in=['A','S','V']).order_by('entrada'),
            "em_desenvolvimento": Issue.objects.filter(status='D').order_by('entrada')
        }
    return render(request,'core/issues.html', args)


@login_required
@permission_required('core.view_alerta')
def alertas(request):
    alertas = None
    if request.method == 'POST':
        alertas = Alerta.objects.filter(usuario=request.POST['user']).order_by('create_at')
        if request.POST['pesquisa'] != '':
            alertas = alertas.filter(titulo__contains=request.POST['pesquisa'])
        if not 'lido' in request.POST:
            alertas = alertas.filter(lido=False)
        if 'critico' in request.POST:
            alertas = alertas.filter(critico=True)
        if request.POST['periodo_de'] != '' or request.POST['periodo_ate'] != '':
            if request.POST['periodo_de'] != '' and request.POST['periodo_ate'] != '':
                alertas = alertas.filter(create_at__range=[request.POST['periodo_de'],request.POST['periodo_ate']])
            elif request.POST['periodo_ate'] != '':
                alertas = alertas.filter(create_at__lte=request.POST['periodo_ate'])
            elif request.POST['periodo_de'] != '':
                alertas = alertas.filter(create_at__gte=request.POST['periodo_de'])
        if not alertas.exists():
            messages.warning(request,'Nenhum alerta com os filtros selecionados')
    return render(request,'core/alertas.html',{'alertas':alertas})

@login_required
@permission_required('core.console')
def console(request):
    if request.method == 'POST':
        response = Run(request, json.loads(request.POST['script']))
        if type(response) is list:
            if response[0]:
                messages.success(request,response[1])
            else:
                messages.error(request,response[1])
        else:
            return render(request, response['path'], response['data'])
    return render(request,'core/console.html')

@login_required
@permission_required('core.view_settings')
def settings(request):
    try: # Busca configuracao do app
        settings = Settings.objects.all().get()
    except: # Caso ainda nao configurado, inicia com configuracao basica
        if Settings.objects.all().count() == 0:
            settings = Settings()
            settings.save()
            l = Log()
            l.modelo = "core.settings"
            l.objeto_id = settings.id
            l.objeto_str = 'n/a'
            l.usuario = request.user
            l.mensagem = "AUTO CREATED"
            l.save()
        else:
            settings = None
            messages.error(request,'<b>Erro::</b> Identificado duplicatas nas configurações do sistema, entre em contato com o administrador.')
    form = SettingsForm(instance=settings)
    return render(request,'core/settings.html',{'form':form,'settings':settings})

# METODOS ADD
@login_required
@permission_required('core.add_empresa')
def empresa_add(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "core.empresa"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Empresa <b>' + registro.nome + '</b> criada')
                return redirect('core_empresas')
            except:
                messages.error(request,'Erro ao inserir empresa [INVALID FORM]')
                return redirect('core_empresas')
    else:
        form = EmpresaForm()
    return render(request,'core/empresa_add.html',{'form':form})

@login_required
@permission_required('auth.add_user')
def usuario_add(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save(commit=False)
                registro.set_password(request.POST['password'])
                registro.save()
                for grupo in request.POST.getlist('grupos'):
                    g = Group.objects.get(id=grupo)
                    g.user_set.add(registro)
                
                for perm in request.POST.getlist('perms'):
                    p = Permission.objects.get(id=perm)
                    p.user_set.add(registro)
                
                for empresa in request.POST.getlist('empresas'):
                    e = Empresa.objects.get(id=empresa)
                    registro.profile.empresas.add(e)
                l = Log()
                l.modelo = "auth.user"
                l.objeto_id = registro.id
                l.objeto_str = registro.username
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Usuario <b>' + registro.username + '</b> criado')
                return redirect('core_usuario_id', registro.id)
            except:
                messages.error(request,'Erro ao inserir usuario [INVALID FORM]')
                return redirect('core_usuarios')
    else:
        form = UserForm()
    return render(request,'core/usuario_add.html',{'form':form})

@login_required
@permission_required('auth.add_group')
def grupo_add(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "auth.group"
                l.objeto_id = registro.id
                l.objeto_str = registro.name
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Grupo <b>' + registro.name + '</b> criado')
                return redirect('core_grupos')
            except:
                messages.error(request,'Erro ao inserir grupo [INVALID FORM]')
                return redirect('core_grupos')
    else:
        form = GroupForm()
    return render(request,'core/grupo_add.html',{'form':form})

@login_required
@permission_required('core.add_agenda')
def agenda_add(request):
    if request.method == 'POST':
        form = AgendaForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                registro = form.save()
                registro.create_by = request.user.username
                registro.save()
                params = {
                    'titulo':'<b class="text-purple">Agenda:</b> Novo evento',
                    'mensagem':f'<b>{registro.titulo}</b><br />Data: <b>{registro.data.strftime("%d/%m/%Y")}</b>',
                    'link': f'core_agenda_id/{registro.id}'
                }
                perm = Permission.objects.get(codename='view_agenda')  
                for participante in registro.participantes.filter(Q(groups__permissions=perm) | Q(user_permissions=perm)).distinct(): # Gera alerta para participantes do evento
                    params['usuario'] = participante
                    Alerta.objects.create(**params)
                l = Log()
                l.modelo = "core.agenda"
                l.objeto_id = registro.id
                l.objeto_str = registro.titulo[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Evento <b>cadastrado</b>')
                return redirect('core_agendas')
            except:
                messages.error(request,'Erro ao inserir agenda [INVALID FORM]')
                return redirect('core_agendas')
    else:
        agenda = Agenda()
        agenda.data = request.GET['data']
        form = AgendaForm(instance=agenda)
    return render(request,'core/agenda_add.html',{'form':form})

@login_required
@permission_required('core.add_feriado')
def feriado_add(request):
    if request.method == 'POST':
        form = FeriadoForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "core.feriado"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Feriado <b>cadastrado</b>')
                return redirect('core_feriado_add')
            except:
                messages.error(request,'Erro ao inserir feriado [INVALID FORM]')
                return redirect('core_feriado_add')
    else:
        form = FeriadoForm()
    return render(request,'core/feriado_add.html',{'form':form})

@login_required
@permission_required('core.add_issue')
def issue_add(request):
    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                # Insere anexos
                has_file_errors = False
                files = []                
                for file in request.FILES.getlist('files'):
                    if validate_file_extension(file):
                        img = Issuefile.objects.create(issue=registro,file=file)
                        files.append(f'<a class="me-3" href="{img.file.url}" target="_blank"><i class="fas fa-camera me-1"></i>{img.file_name()}</a>')
                    else:
                        has_file_errors = True
                # Ajusta demais informacoes do registro
                registro.usuario = request.user
                if request.user.has_perm('core.eh_suporte'): # Se proprio analista abrir o chamado, ja vincula tambem como analista
                    registro.analista = request.user
                entry = [{
                        "data": date.today().strftime("%d/%m"),
                        "hora": datetime.now().strftime("%H:%M"),
                        "origem": 0 if request.user.has_perm('core.eh_suporte') else 1,
                        "usuario": request.user.username,
                        "files": files,
                        "mensagem": request.POST['nova_interacao']
                    }]
                registro.historico = json.dumps(entry)
                registro.save()
                l = Log()
                l.modelo = "core.issue"
                l.objeto_id = registro.id
                l.objeto_str = registro.assunto
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                if not has_file_errors:
                    messages.success(request,'Issue <b>cadastrado</b>')
                else:
                    messages.warning(request,'Issue <b>cadastrado</b> porém alguns arquivos tem extensão não aceita e foram descartados.')
                return redirect('core_issue_id', registro.id)
            except:
                messages.error(request,'Erro ao inserir issue [INVALID FORM]')
                return redirect('core_issue_add')
    else:
        form = IssueForm()
    return render(request,'core/issue_add.html',{'form':form})

# METODOS GET
@login_required
@permission_required('core.change_empresa')
def empresa_id(request, id):
    empresa = Empresa.objects.get(id=id)
    form = EmpresaForm(instance=empresa)
    return render(request,'core/empresa_id.html',{'form':form,'empresa':empresa})

@login_required
@permission_required('auth.change_user')
def usuario_id(request, id):
    usuario = User.objects.get(id=id)
    form = UserForm(instance=usuario)
    return render(request,'core/usuario_id.html',{'form':form,'usuario':usuario})

@login_required
@permission_required('auth.change_group')
def grupo_id(request, id):
    grupo = Group.objects.get(id=id)
    form = GroupForm(instance=grupo)
    return render(request,'core/grupo_id.html',{'form':form,'grupo':grupo})

@login_required
@permission_required('core.view_alerta')
def alerta_id(request, id):
    alerta = Alerta.objects.get(id=id)
    return render(request,'core/alerta_id.html',{'alerta':alerta})

@login_required
@permission_required('core.view_agenda')
def agenda_id(request, id):
    agenda = Agenda.objects.get(id=id)
    form = AgendaForm(instance=agenda)
    return render(request,'core/agenda_id.html',{'form':form,'agenda':agenda})

@login_required
@permission_required('core.view_feriado')
def feriado_id(request, id):
    feriado = Feriado.objects.get(id=id)
    form = FeriadoForm(instance=feriado)
    return render(request,'core/feriado_id.html',{'form':form,'feriado':feriado})

@login_required
@permission_required('core.view_issue')
def issue_id(request, id):
    issue = Issue.objects.get(id=id)
    form = IssueForm(instance=issue)
    return render(request,'core/issue_id.html',{'form':form,'issue':issue})

# METODOS UPDATE
@login_required
@permission_required('core.change_empresa')
def empresa_update(request, id):
    empresa = Empresa.objects.get(pk=id)
    form = EmpresaForm(request.POST, request.FILES, instance=empresa)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "core.empresa"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Empresa <b>' + registro.nome + '</b> alterada')
        return redirect('core_empresa_id',id)
    else:
        return render(request,'core/empresa_id.html',{'form':form,'empresa':empresa})

@login_required
@permission_required('auth.change_user')
def usuario_update(request, id):
    usuario = User.objects.get(pk=id)
    form = UserForm(request.POST, instance=usuario)
    if form.is_valid():
        registro = form.save(commit=False)
        if 'force_password_change' in request.POST:
            registro.profile.force_password_change = True
        else:
            registro.profile.force_password_change = False
        
        if 'reset_password' in request.POST and request.POST['reset_password'] != '':
            registro.set_password(request.POST['reset_password'])
            registro.profile.force_password_change = True
            
        registro.save()
        registro.groups.clear()
        for grupo in request.POST.getlist('grupos'):
            g = Group.objects.get(id=grupo)
            g.user_set.add(registro)
        
        registro.user_permissions.clear()
        for perm in request.POST.getlist('perms'):
            p = Permission.objects.get(id=perm)
            p.user_set.add(registro)
        
        registro.profile.empresas.clear()
        for empresa in request.POST.getlist('empresas'):
            e = Empresa.objects.get(id=empresa)
            registro.profile.empresas.add(e)
        l = Log()
        l.modelo = "auth.user"
        l.objeto_id = registro.id
        l.objeto_str = registro.username
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Usuario <b>' + registro.username + '</b> alterado')
        return redirect('core_usuario_id',id)
    else:
        return render(request,'core/usuario_id.html',{'form':form,'usuario':usuario})

@login_required
@permission_required('auth.change_group')
def grupo_update(request, id):
    grupo = Group.objects.get(pk=id)
    form = GroupForm(request.POST, instance=grupo)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "auth.group"
        l.objeto_id = registro.id
        l.objeto_str = registro.name
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Grupo <b>' + registro.name + '</b> alterado')
        return redirect('core_grupo_id',id)
    else:
        return render(request,'core/grupo_id.html',{'form':form,'grupo':grupo})

@login_required
def alerta_marcar_lido(request):
    alerta = Alerta.objects.get(id=request.GET.get('id', None))
    alerta.lido = True
    alerta.lido_at = datetime.now()
    alerta.save()
    return HttpResponse('')

@login_required
@permission_required('core.change_agenda')
def agenda_update(request, id):
    agenda = Agenda.objects.get(pk=id)
    form = AgendaForm(request.POST, request.FILES, instance=agenda)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "core.agenda"
        l.objeto_id = registro.id
        l.objeto_str = registro.titulo
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Evento alterada')
        return redirect('core_agenda_id',id)
    else:
        return render(request,'core/agenda_id.html',{'form':form,'agenda':agenda})

@login_required
@permission_required('core.change_feriado')
def feriado_update(request, id):
    feriado = Feriado.objects.get(pk=id)
    form = FeriadoForm(request.POST, instance=feriado)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "core.feriado"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Feriado <b>{registro.nome}</b> alterado')
        return redirect('core_feriado_id',id)
    else:
        return render(request,'core/feriado_id.html',{'form':form,'feriado':feriado})

@login_required
@permission_required('core.change_issue')
def issue_update(request, id):
    issue = Issue.objects.get(pk=id)
    form = IssueForm(request.POST, instance=issue)
    if form.is_valid():
        registro = form.save()
        # Insere anexos
        has_file_errors = False
        files = []
        for file in request.FILES.getlist('files'):
            if validate_file_extension(file):
                img = Issuefile.objects.create(issue=registro,file=file)
                files.append(f'<a class="me-3" href="{img.file.url}" target="_blank"><i class="fas fa-camera me-1"></i>{img.file_name()}</a>')
            else:
                has_file_errors = True
        # Ajusta demais informacoes do registro
        registro.ultima_interacao = datetime.now()
        if registro.analista == None and request.user.has_perm('core.eh_suporte'): # Atribui o primeiro analista a responder o chamado
                    registro.analista = request.user
        if request.POST['nova_interacao'] != '' or len(files) > 0:
            entry = {
                    "data": date.today().strftime("%d/%m"),
                    "hora": datetime.now().strftime("%H:%M"),
                    "origem": 0 if request.user.has_perm('core.eh_suporte') else 1,
                    "usuario": request.user.username,
                    "files": files,
                    "mensagem": request.POST['nova_interacao'] if issue.status != 'F' else '[ FECHADO ] ' + request.POST['nova_interacao']
                }
            history = json.loads(registro.historico)
            history.insert(0, entry)
            registro.historico = json.dumps(history)
        registro.save()
        try: # Carrega configuracoes do app
            settings = Settings.objects.all().get()
        except: # Caso nao gerado configuracoes iniciais carrega definicoes basicas
            settings = Settings()
        
        if settings.gera_notificacao_issue_atualizado:
            for user in registro.followers.exclude(id=request.user.id):
                args = {
                    "titulo": f"<i class='fas fa-bug me-2'></i>Issue {registro.id} atualizado",
                    "mensagem": f'<b class="text-secondary">{registro.get_tipo_display()}</b> - <b>{registro.usuario.username.title()}</b><br>{registro.assunto}',
                    "link": f'/core_issue_id/{registro.id}',
                    "usuario": user
                }
                Alerta.objects.create(**args)
        l = Log()
        l.modelo = "core.issue"
        l.objeto_id = registro.id
        l.objeto_str = registro.assunto
        l.usuario = request.user
        l.mensagem = "UPDATE" if issue.status != 'F' else "CLOSED"
        l.save()
        if not has_file_errors:
            messages.success(request,f'Issue <b>{registro.id}</b> atualizado')
        else:
            messages.warning(request,'Issue <b>atualizado</b> porém alguns arquivos tem extensão não aceita e foram descartados.')
        return redirect('core_issue_id',id)
    else:
        return render(request,'core/issue_id.html',{'form':form,'issue':issue})

@login_required
@permission_required('core.change_settings')
def settings_update(request, id):
    settings = Settings.objects.get(pk=id)
    form = SettingsForm(request.POST, instance=settings)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "core.settings"
        l.objeto_id = registro.id
        l.objeto_str = 'n/a'
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Settings <b>CORE</b> alterado')
        return redirect('core_settings')
    else:
        return render(request,'core/settings.html',{'form':form,'settings':settings})

# METODOS DELETE
@login_required
@permission_required('core.delete_empresa')
def empresa_delete(request, id):
    try:
        registro = Empresa.objects.get(pk=id)
        l = Log()
        l.modelo = "core.empresa"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,'Empresa <b>' + registro.nome + '</b> apagada')
        return redirect('core_empresas')
    except:
        messages.error(request,'ERRO ao apagar empresa')
        return redirect('core_empresa_id', id)

@login_required
@permission_required('auth.delete_user')
def usuario_delete(request, id):
    try:
        registro = User.objects.get(pk=id)
        l = Log()
        l.modelo = "auth.user"
        l.objeto_id = registro.id
        l.objeto_str = registro.username
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,'Usuario <b>' + registro.username + '</b> apagado')
        return redirect('core_usuarios')
    except:
        messages.error(request,'ERRO ao apagar usuario')
        return redirect('core_usuario_id', id)

@login_required
@permission_required('auth.delete_group')
def grupo_delete(request, id):
    try:
        registro = Group.objects.get(pk=id)
        l = Log()
        l.modelo = "auth.group"
        l.objeto_id = registro.id
        l.objeto_str = registro.name
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,'Grupo <b>' + registro.name + '</b> apagado')
        return redirect('core_grupos')
    except:
        messages.error(request,'ERRO ao apagar grupo')
        return redirect('core_grupo_id', id)

@login_required
@permission_required('core.delete_alerta')
def alerta_delete(request, id):
    try:
        registro = Alerta.objects.get(pk=id)
        registro.delete()
        messages.warning(request,'Alerta <b>apagado</b>')
        return redirect('core_alertas')
    except:
        messages.error(request,'ERRO ao apagar alerta')
        return redirect('core_alerta_id', id)

@login_required
@permission_required('core.delete_agenda')
def agenda_delete(request, id):
    try:
        registro = Agenda.objects.get(pk=id)
        l = Log()
        l.modelo = "core.agenda"
        l.objeto_id = registro.id
        l.objeto_str = registro.titulo
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Evento apagado')
        return redirect('core_agendas')
    except:
        messages.error(request,'ERRO ao apagar evento')
        return redirect('core_agenda_id', id)

@login_required
@permission_required('core.delete_feriado')
def feriado_delete(request, id):
    try:
        registro = Feriado.objects.get(pk=id)
        l = Log()
        l.modelo = "core.feriado"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Feriado <b>{registro.nome}</b> apagado')
        return redirect('core_feriados')
    except:
        messages.error(request,'ERRO ao apagar feriado')
        return redirect('core_feriado_id', id)

@login_required
@permission_required('core.delete_issue')
def issue_delete(request, id):
    try:
        registro = Issue.objects.get(pk=id)
        l = Log()
        l.modelo = "core.issue"
        l.objeto_id = registro.id
        l.objeto_str = registro.assunto
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Issue <b>apagado</b>.')
        return redirect('core_issues')
    except:
        messages.error(request,'ERRO ao apagar issue')
        return redirect('core_issue_id', id)


# AUTENTICACAO E PERMISSAO
def login(request):
    return render(request,'core/login.html')

def authenticate(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            user = auth.authenticate(request, username=username, password=password)
            if user is not None:
                auth.login(request, user)
                return redirect('index')
    messages.error(request,'Falha na autenticação.')
    return redirect('login')

@login_required
def change_password(request):
    try: # Carrega configuracoes do app
        settings = Settings.objects.all().get()
    except: # Caso nao gerado configuracoes iniciais carrega definicoes padrao
        settings = Settings()
    if request.method == 'POST':
        password_current = request.POST['password_current']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']

        if request.user.check_password(password_current):
            if password == password_confirm:
                if password_current != password:
                    if password_valid(password):
                        request.user.set_password(password)
                        request.user.profile.force_password_change = False
                        request.user.save()
                        messages.success(request, 'Senha alterada')
                        return redirect('login')
                    else:
                        messages.error(request,'Senha não atende aos requisitos mínimos')
                else:
                    messages.error(request, 'Nova senha não pode ser igual a senha atual')
            else:
                messages.error(request, 'Senhas nova e confirmação não são iguais')
        else:
            messages.error(request, 'Senha atual não confere')
        return render(request,'core/change_password.html')
    else:
        return render(request,'core/change_password.html', {'settings':settings})

def logout(request):
    auth.logout(request)
    return redirect('index')

@login_required
def handler(request, code):
    return render(request,f'{code}.html')


def password_valid(password):
    try: # Carrega configuracoes do app
        settings = Settings.objects.all().get()
    except: # Caso nao gerado configuracoes iniciais carrega definicoes basicas
        settings = Settings()

    if len(password) < settings.quantidade_caracteres_senha:
        return False
    if settings.senha_exige_numero and re.search('[0-9]',password) is None:
        return False
    if settings.senha_exige_alpha and re.search('[a-z]',password, re.IGNORECASE) is None:
        return False
    if settings.senha_exige_caractere and re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]", password) is None:
        return False
    else:
        return True

# AJAX METODOS

# app_data Manipula arquivos json salvos no diretorio app_data
# --
# @version  1.0
# @since    31/08/2022
# @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
# @param    {String} fpath Path relativo do arquivo alvo
@login_required
def app_data(request, fpath): 
    if request.method == 'GET': # Requisicao, abre arquivo (se existir) e retorna conteudo (em json)
        try:
            f = open(f'{settings.APP_DATA}/{fpath}', 'r', encoding='utf-8')
            data = json.load(f)
            f.close()
        except Exception as e:
            data = ''
        return JsonResponse(json.dumps(data), safe=False)
    elif request.method == 'POST': # Modo de gravacao, atualiza (ou cria arquivo) com conteudo enviado
        try:
            f = open(f'{settings.APP_DATA}/{fpath}', 'w', encoding='utf-8')
            f.write(json.dumps(json.load(request), ensure_ascii=False))
            f.close()
        except Exception as e:
            pass
    return HttpResponse('')


@login_required
def get_empresas(request):
    # Metodo retorna JSON com dados das empresas
    try:
        if request.GET.get('usuario', None) == 'new':
            empresas = Empresa.objects.all().order_by('nome')
        else:
            usuario = request.user if request.GET.get('usuario', None) == None else User.objects.get(id=request.GET.get('usuario', None))
            empresas = usuario.profile.empresas.all().order_by('nome')
        itens = []
        for item in empresas:
            item_dict = vars(item) # Converte objetos em dicionario
            if '_state' in item_dict: del item_dict['_state'] # Remove _state do dict (se existir)
            itens.append(item_dict)
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

@login_required
def get_usuarios(request):
    try:
        usuarios = User.objects.all().order_by('username')
        if not request.GET.get('inativos', None):
            usuarios = usuarios.filter(is_active=True)
        data = serializers.serialize('json', usuarios)
        return HttpResponse(data, content_type="application/json")
    except:
        return HttpResponse('')

@login_required
def get_grupos(request):
    try:
        if request.GET.get('usuario', None) == 'new':
            grupos = Group.objects.all().order_by('name')
        else:
            usuario = request.user if request.GET.get('usuario', None) == None else User.objects.get(id=request.GET['usuario'])
            grupos = Group.objects.filter(user=usuario).order_by('name')
        itens = []
        for item in grupos:
            item_dict = vars(item) # Converte objeto em dicionario
            if '_state' in item_dict: del item_dict['_state'] # Remove _state do dict (se existir)
            itens.append(item_dict)
        dataJSON = json.dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

@login_required
def get_user_perms(request):
    try:
        exclude_itens = ['sessions','contenttypes','admin']
        if request.GET.get('usuario', None) == 'new':
            perms = Permission.objects.all().exclude(content_type__app_label__in=exclude_itens).order_by('content_type__app_label', 'content_type__model', 'name')
        else:
            usuario = request.user if request.GET.get('usuario', None) == None else User.objects.get(id=request.GET['usuario'])
            perms = Permission.objects.filter(user=usuario).exclude(content_type__app_label__in=exclude_itens).order_by('content_type__app_label', 'content_type__model', 'name')
        itens = []
        for item in perms:
            item_dict = {'id':item.id,'nome':f'{item.content_type.app_label} | {item.content_type.model} | {item.name}'}
            itens.append(item_dict)
        dataJSON = json.dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

@login_required
def get_group_perms(request):
    try:
        tipo = request.GET.get('tipo',None)
        if request.GET.get('grupo',None) != 'new':
            grupo = Group.objects.get(id=request.GET.get('grupo',None))
            if tipo == 'disponiveis':
                perms = Permission.objects.all().exclude(group=grupo).order_by('content_type__app_label', 'content_type__model', 'name')
            elif tipo == 'cadastrados':
                perms = Permission.objects.all().filter(group=grupo).order_by('content_type__app_label', 'content_type__model', 'name')
            else:
                pass
        else:
            exclude_itens = ['admin','contenttypes','sessions']
            perms = Permission.objects.all().exclude(content_type__app_label__in=exclude_itens).order_by('content_type__app_label', 'content_type__model', 'name')
        itens = {}
        for item in perms:
            itens[f'{item.content_type.app_label} | {item.content_type.model} | {item.name}'] = item.id
        dataJSON = json.dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

@login_required
def get_alertas(request):
    alertas = Alerta.objects.filter(usuario=request.user,lido=False).order_by('create_at')
    data = serializers.serialize('json', alertas)
    return HttpResponse(data, content_type="application/json")

@login_required
@permission_required('core.view_agenda')
def get_agenda(request):
    ano = request.GET.get('ano', date.today().year)
    mes = request.GET.get('mes', date.today().month)
    agenda = Agenda.objects.filter(data__year=ano,data__month=mes,participantes=request.user).order_by('data','inicio','termino')
    obj = serializers.serialize('json', agenda)
    return HttpResponse(obj, content_type="application/json")

@login_required
def get_feriados(request):
    ano = request.GET.get('ano', date.today().year)
    feriados = Feriado.objects.filter(data__year=ano).order_by('data')
    list = {}
    for feriado in feriados:
        list[feriado.data.strftime("%Y-%m-%d")] = feriado.nome
    obj = json.dumps(list)
    return HttpResponse(obj, content_type="application/json")

@login_required
def get_contenttypes(request):
    try:
        exclude_itens = ['admin','auth','contenttypes','sessions']
        contenttypes = ContentType.objects.all().exclude(app_label__in=exclude_itens).order_by('app_label','model')
        itens = {}
        for item in contenttypes:
            itens[item.app_label + '.' + item.model] = item.id
        dataJSON = json.dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')