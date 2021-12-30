import re
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import auth, messages
from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Empresa, Log, Alerta
from .forms import EmpresaForm, UserForm, GroupForm
from datetime import datetime
from django.http import HttpResponse
from django.core import serializers
from json import dumps
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
    if request.method == 'POST':
        grupos = grupos.filter(name__contains=request.POST['pesquisa'])
    return render(request,'core/grupos.html',{'grupos':grupos})

@login_required
@permission_required('auth.view_user')
def usuarios(request):
    usuarios = User.objects.all().order_by('username')
    if request.method == 'POST':
        if request.POST['pesquisa'] != '':
            if request.POST['pesquisa'][-1] == '*':
                if request.POST['pesquisa'] == 'super*':
                    usuarios = usuarios.filter(is_superuser=True)
                elif request.POST['pesquisa'] == 'membro*':
                    usuarios = usuarios.filter(is_staff=True)
                elif request.POST['pesquisa'] == 'inativo*':
                    usuarios = usuarios.filter(is_active=False)
            else:
                usuarios = usuarios.filter(username__contains=request.POST['pesquisa'])
    return render(request,'core/usuarios.html',{'usuarios':usuarios})

@login_required
@permission_required('core.view_log')
def logs(request):
    target_model = request.GET.get('target_model',None)
    mensagem = request.GET.get('mensagem',None)
    logs = Log.objects.filter(modelo=target_model,mensagem=mensagem)
    return render(request,'core/logs.html',{'logs':logs})

@login_required
def docs(request):
    return render(request,'core/docs/core.html')

@login_required
@permission_required('core.console')
def console(request):
    h = datetime.now().strftime('%H:%M:%S')
    c = ''
    if request.method == 'POST':
        print('ENTREO NO POST')
        from .console import Run
        response = Run(request.POST['script'])
        for r in response:
            c += f'<p class="m-0 d-flex justify-content-between"><span>{r}</span><span>{h}</span></p>'
    else:
        c = f'<p class="m-0 d-flex justify-content-between"><span>Console DOT system <b>versão 1.0</b>, powered by <a href="https://ace.c9.io/" target="_blank" class="text-danger fw-bold text-decoration-none">Ace Editor&trade;</a></span><span>{h}</span></p>'
    return render(request,'core/console.html',{'console':c})


# METODOS ADD
@login_required
@permission_required('core.add_empresa')
def empresa_add(request):
    if request.method == 'POST':
        form = EmpresaForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "core.empresa"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Empresa ' + registro.nome + ' criada')
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
                form_clean = form.cleaned_data
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
                messages.success(request,'Usuario ' + registro.username + ' criado')
                return redirect('core_usuarios')
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
            # try:
            form_clean = form.cleaned_data
            registro = form.save()
            l = Log()
            l.modelo = "auth.group"
            l.objeto_id = registro.id
            l.objeto_str = registro.name
            l.usuario = request.user
            l.mensagem = "CREATED"
            l.save()
            messages.success(request,'Grupo ' + registro.name + ' criado')
            return redirect('core_grupos')
            # except:
            #     messages.error(request,'Erro ao inserir grupo [INVALID FORM]')
            #     return redirect('core_grupos')
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
    logs = Log.objects.filter(modelo='auth.group',objeto_id=grupo.id).order_by('-data')[:15]
    return render(request,'core/grupo_id.html',{'form':form,'grupo':grupo,'logs':reversed(logs)})


# METODOS UPDATE
@login_required
@permission_required('core.change_empresa')
def empresa_update(request, id):
    empresa = Empresa.objects.get(pk=id)
    form = EmpresaForm(request.POST, instance=empresa)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "core.empresa"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Empresa ' + registro.nome + ' alterada')
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
        messages.success(request,'Usuario ' + registro.username + ' alterado')
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
        messages.success(request,'Grupo ' + registro.name + ' alterado')
        return redirect('core_grupo_id',id)
    else:
        return render(request,'core/grupo_id.html',{'form':form,'grupo':grupo})

@login_required
def alerta_marcar_lido(request):
    alerta = Alerta.objects.get(id=request.GET.get('id', None))
    alerta.lido = True
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
        l.save()
        registro.delete()
        messages.warning(request,'Empresa ' + registro.nome + ' apagada')
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
        l.save()
        registro.delete()
        messages.warning(request,'Usuario ' + registro.username + ' apagado')
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
        l.save()
        registro.delete()
        messages.warning(request,'Grupo ' + registro.name + ' apagado')
        return redirect('core_grupos')
    except:
        messages.error(request,'ERRO ao apagar grupo')
        return redirect('core_grupo_id', id)

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

def handle404(request):
    return render(request,'404.html')

def handle500(request):
    return render(request,'500.html')

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
def get_empresas(request):
    try:
        tipo = request.GET.get('tipo',None)
        if request.GET.get('usuario',None) != 'new':
            usuario = User.objects.get(id=request.GET.get('usuario',None))
            if tipo == 'disponiveis':
                empresas = Empresa.objects.all().exclude(profile__user=usuario).order_by('nome')
            elif tipo == 'cadastrados':
                empresas = usuario.profile.empresas.all().order_by('nome')
            else:
                pass
        else:
            empresas = Empresa.objects.all().order_by('nome')
        itens = {}
        for item in empresas:
            itens[item.nome] = item.id
        dataJSON = dumps(itens)
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
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

@login_required
def get_user_perms(request):
    try:
        tipo = request.GET.get('tipo',None)
        if request.GET.get('usuario',None) != 'new':
            usuario = User.objects.get(id=request.GET.get('usuario',None))
            if tipo == 'disponiveis':
                perms = Permission.objects.all().exclude(user=usuario).order_by('id')
            elif tipo == 'cadastrados':
                perms = Permission.objects.all().filter(user=usuario).order_by('id')
            else:
                pass
        else:
            perms = Permission.objects.all().exclude(content_type__app_label='sessions').exclude(content_type__app_label='contenttypes').exclude(content_type__app_label='admin').order_by('id')
        itens = {}
        for item in perms:
            itens[item.codename] = item.id
        dataJSON = dumps(itens)
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
                perms = Permission.objects.all().exclude(group=grupo).order_by('id')
            elif tipo == 'cadastrados':
                perms = Permission.objects.all().filter(group=grupo).order_by('id')
            else:
                pass
        else:
            exclude_itens = ['admin','contenttypes','sessions']
            perms = Permission.objects.all().exclude(content_type__app_label__in=exclude_itens).order_by('id')
        itens = {}
        for item in perms:
            itens[item.codename] = item.id
        dataJSON = dumps(itens)
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
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')