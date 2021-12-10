import re
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import auth, messages
from django.contrib.auth.models import User
from .models import Empresa, Log
from .forms import EmpresaForm
from django.http import HttpResponse
from json import dumps
from django.core.serializers.json import DjangoJSONEncoder


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
@permission_required('core.view_log')
def logs(request):
    modelo = request.GET.get('modelo',None)
    mensagem = request.GET.get('mensagem',None)
    logs = Log.objects.filter(modelo=modelo,mensagem=mensagem)
    return render(request,'core/logs.html',{'logs':logs})
    
def run_script(request):
    # from plan.models import Diaria
    # usuario = User.objects.get(id=1)
    # usuario.profile.force_password_change = False
    # usuario.save()
    # messages.warning(request,'Done')
    messages.warning(request,'Nothing to do')
    return redirect('index')


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


# METODOS GET
@login_required
@permission_required('core.change_empresa')
def empresa_id(request, id):
    empresa = Empresa.objects.get(id=id)
    form = EmpresaForm(instance=empresa)
    return render(request,'core/empresa_id.html',{'form':form,'empresa':empresa})


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
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Empresa ' + registro.nome + ' alterada')
        return redirect('core_empresa_id',id)
    else:
        return render(request,'core/empresa_id.html',{'form':form,'empresa':empresa})

# METODOS DELETE
@login_required
@permission_required('core.delete_empresa')
def empresa_delete(request, id):
    try:
        registro = Empresa.objects.get(pk=id)
        l = Log()
        l.modelo = "core.empresa"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Empresa ' + registro.nome + ' apagada')
        return redirect('core_empresas')
    except:
        messages.error(request,'ERRO ao apagar empresa')
        return redirect('core_empresa_id', id)

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
        empresas = Empresa.objects.all()
        itens = {}
        for item in empresas:
            itens[item.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')