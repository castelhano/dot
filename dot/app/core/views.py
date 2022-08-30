import re
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import auth, messages
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Empresa, Log, Alerta
from .forms import EmpresaForm, UserForm, GroupForm
from .extras import clean_request
from .console import Run
from datetime import datetime
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.conf import settings
# from django.core.serializers.json import DjangoJSONEncoder


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
def docs(request, page='core'):
    return render(request,f'core/docs/{page}.html')

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
        
        try:
            if request.POST['reset_password'] != '':
                registro.set_password(request.POST['reset_password'])
                registro.profile.force_password_change = True
        except:
            # CAMPO RESET PASSWORD EH POR PADRAO DISABLED NO FORM, EXCEPT TRATA AUSENCIA DO CAMPO NO POST
            pass
            
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
                        messages.error(request,'Senha deve ter 8 digitos, conter letras e números')
                else:
                    messages.error(request, 'Nova senha não pode ser igual a senha atual')
            else:
                messages.error(request, 'Senhas nova e confirmação não são iguais')
        else:
            messages.error(request, 'Senha atual não confere')
        return render(request,'core/change_password.html')
    else:
        return render(request,'core/change_password.html')

def logout(request):
    auth.logout(request)
    return redirect('index')

def handler(request, code):
    return render(request,f'{code}.html')

def password_valid(password):
    if len(password) < 8:
        return False
    if re.search('[0-9]',password) is None:
        return False
    if re.search('[a-z]',password) is None and re.search('[A-Z]',password) is None:
        return False
    else:
        return True

# AJAX METODOS
@login_required
def app_data(request, fpath):
    try:
        f = open(f'{settings.APP_DATA}/{fpath}', 'r', encoding='utf-8')
        data = json.load(f)
        f.close()
    except Exception as e:
        data = []
    return JsonResponse(json.dumps(data), safe=False)

@login_required
def get_empresas(request):
    try:
        tipo = request.GET.get('tipo',None)
        if request.GET.get('usuario', None) == 'new':
            usuario = User()
        else:
            usuario = request.user if request.GET.get('usuario', None) == None else User.objects.get(id=request.GET.get('usuario', None))
        # if usuario.is_superuser: # Caso superusuario retorna todas as empresas
        #     empresas = Empresa.objects.all().order_by('nome')
        if tipo == None or tipo == 'cadastrados': # Retorna as empresas cadastradas para usuario
            empresas = usuario.profile.empresas.all().order_by('nome')
        elif tipo == 'disponiveis':
            if request.GET.get('usuario', None) == 'new':
                empresas = Empresa.objects.all().order_by('nome')
            else:
                empresas = Empresa.objects.all().exclude(profile__user=usuario).order_by('nome')
        else:
            empresas = None
        itens = {}
        for item in empresas:
            itens[item.nome] = item.id
        dataJSON = json.dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

@login_required
def get_usuarios(request):
    try:
        inativos = request.GET.get('inativos', None)
        usuarios = User.objects.all().order_by('username')
        if not request.GET.get('inativos', None):
            usuarios = usuarios.filter(is_active=True)
        itens = {}
        for item in usuarios:
            itens[item.username] = item.id
        dataJSON = json.dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

@login_required
def get_grupos(request):
    try:
        tipo = request.GET.get('tipo',None)
        if request.GET.get('usuario',None) != 'new':
            usuario = User.objects.get(id=request.GET.get('usuario',None))
            if tipo == 'disponiveis':
                grupos = Group.objects.all().exclude(user=usuario).order_by('name')
            elif tipo == 'cadastrados':
                grupos = usuario.groups.all().order_by('name')
            else:
                pass
        else:
            grupos = Group.objects.all().order_by('name')
        itens = {}
        for item in grupos:
            itens[item.name] = item.id
        dataJSON = json.dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

@login_required
def get_user_perms(request):
    try:
        tipo = request.GET.get('tipo',None)
        exclude_itens = ['sessions','contenttypes','admin']
        if request.GET.get('usuario',None) != 'new':
            usuario = User.objects.get(id=request.GET.get('usuario',None))
            if tipo == 'disponiveis':
                perms = Permission.objects.all().exclude(user=usuario).exclude(content_type__app_label__in=exclude_itens).order_by('content_type__app_label', 'content_type__model', 'name')
            elif tipo == 'cadastrados':
                perms = Permission.objects.all().filter(user=usuario).exclude(content_type__app_label__in=exclude_itens).order_by('content_type__app_label', 'content_type__model', 'name')
            else:
                pass
        else:
            perms = Permission.objects.all().exclude(content_type__app_label__in=exclude_itens).order_by('content_type__app_label', 'content_type__model', 'name')
        itens = {}
        for item in perms:
            itens[f'{item.content_type.app_label} | {item.content_type.model} | {item.name}'] = item.id
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