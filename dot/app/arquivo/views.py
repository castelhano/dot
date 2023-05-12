from json import dumps as json_dumps
from .models import Container, Grupo, Limite, Ativo, File
from .forms import ContainerForm, GrupoForm, LimiteForm, AtivoForm, FileForm
from core.models import Log
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, permission_required
from datetime import date, timedelta


@login_required
@permission_required('arquivo.view_grupo', login_url="/handler/403")
def grupos(request):
    grupos = Grupo.objects.all().order_by('nome')
    return render(request, 'arquivo/grupos.html', {'grupos':grupos})

@login_required
@permission_required('arquivo.view_container', login_url="/handler/403")
def containers(request):
    containers = Container.objects.all().order_by('nome')
    return render(request, 'arquivo/containers.html', {'containers':containers})

@login_required
@permission_required('arquivo.view_limite', login_url="/handler/403")
def limites(request):
    limites = Limite.objects.all().order_by('empresa__nome')
    return render(request, 'arquivo/limites.html', {'limites':limites})

@login_required
@permission_required('arquivo.view_ativo', login_url="/handler/403")
def ativos(request):
    if request.GET.get('search', None):
        return render(request, 'arquivo/ativos_search.html')
    else:
        fisicos = Ativo.objects.filter(fisico=True).count()
        digitais = Ativo.objects.filter(fisico=False).count()
        return render(request, 'arquivo/ativos.html', {'fisicos':fisicos,'digitais':digitais})

# Metodos ADD
@login_required
@permission_required('arquivo.add_grupo', login_url="/handler/403")
def grupo_add(request):
    if request.method == 'POST':
        form = GrupoForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "arquivo.grupo"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Grupo <b>{registro.nome}</b> criado')
                return redirect('arquivo_grupo_add')
            except:
                pass
    else:
        form = GrupoForm()
    return render(request,'arquivo/grupo_add.html',{'form':form})

@login_required
@permission_required('arquivo.add_container', login_url="/handler/403")
def container_add(request):
    if request.method == 'POST':
        form = ContainerForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "arquivo.container"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Container <b>{registro.nome}</b> criado')
                return redirect('arquivo_container_add')
            except:
                pass
    else:
        form = ContainerForm()
    return render(request,'arquivo/container_add.html',{'form':form})

@login_required
@permission_required('arquivo.add_limite', login_url="/handler/403")
def limite_add(request):
    if request.method == 'POST':
        form = LimiteForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "arquivo.limite"
                l.objeto_id = registro.id
                l.objeto_str = registro.empresa.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Limite definido para empresa <b>{registro.empresa.nome}</b>')
                return redirect('arquivo_limite_add')
            except:
                pass
    else:
        form = LimiteForm()
    return render(request,'arquivo/limite_add.html',{'form':form})

@login_required
@permission_required('arquivo.add_ativo', login_url="/handler/403")
def ativo_add(request):
    if request.method == 'POST':
        form = AtivoForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save(commit=False)
                registro.entrada = date.today()
                registro.created_by = request.user
                if registro.grupo.tempo_guarda > 0:
                    delta = registro.grupo.tempo_guarda * 30
                    registro.vencimento = registro.entrada + timedelta(days=delta)
                registro.save()
                l = Log()
                l.modelo = "arquivo.ativo"
                l.objeto_id = registro.id
                l.objeto_str = registro.id
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Ativo <b>{registro.id}</b> criado')
                return redirect('arquivo_ativos')
            except:
                pass
    else:
        form = AtivoForm()
    return render(request,'arquivo/ativo_add.html',{'form':form})

    
# Metodos GET
@login_required
@permission_required('arquivo.change_grupo', login_url="/handler/403")
def grupo_id(request,id):
    grupo = Grupo.objects.get(pk=id)
    form = GrupoForm(instance=grupo)
    return render(request,'arquivo/grupo_id.html',{'form':form,'grupo':grupo})

@login_required
@permission_required('arquivo.change_container', login_url="/handler/403")
def container_id(request,id):
    container = Container.objects.get(pk=id)
    form = ContainerForm(instance=container)
    return render(request,'arquivo/container_id.html',{'form':form,'container':container})

@login_required
@permission_required('arquivo.change_limite', login_url="/handler/403")
def limite_id(request,id):
    limite = Limite.objects.get(pk=id)
    form = LimiteForm(instance=limite)
    return render(request,'arquivo/limite_id.html',{'form':form,'limite':limite})

@login_required
@permission_required('arquivo.change_ativo', login_url="/handler/403")
def ativo_id(request,id):
    ativo = Ativo.objects.get(pk=id)
    form = AtivoForm(instance=ativo)
    return render(request,'arquivo/ativo_id.html',{'form':form,'ativo':ativo})


# Metodos UPDATE
@login_required
@permission_required('arquivo.change_grupo', login_url="/handler/403")
def grupo_update(request,id):
    grupo = Grupo.objects.get(pk=id)
    form = GrupoForm(request.POST, instance=grupo)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "arquivo.grupo"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Grupo <b>' + registro.nome + '</b> alterado')
        return redirect('arquivo_grupo_id', id)
    else:
        return render(request,'arquivo/grupo_id.html',{'form':form,'grupo':grupo})

@login_required
@permission_required('arquivo.change_container', login_url="/handler/403")
def container_update(request,id):
    container = Container.objects.get(pk=id)
    form = ContainerForm(request.POST, instance=container)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "arquivo.container"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Container <b>' + registro.nome + '</b> alterado')
        return redirect('arquivo_container_id', id)
    else:
        return render(request,'arquivo/container_id.html',{'form':form,'container':container})

@login_required
@permission_required('arquivo.change_limite', login_url="/handler/403")
def limite_update(request,id):
    limite = Limite.objects.get(pk=id)
    form = LimiteForm(request.POST, instance=limite)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "arquivo.limite"
        l.objeto_id = registro.id
        l.objeto_str = registro.empresa.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Limite empresa <b>' + registro.empresa.nome + '</b> alterado')
        return redirect('arquivo_limite_id', id)
    else:
        return render(request,'arquivo/limite_id.html',{'form':form,'limite':limite})

@login_required
@permission_required('arquivo.change_ativo', login_url="/handler/403")
def ativo_update(request,id):
    ativo = Ativo.objects.get(pk=id)
    form = AtivoForm(request.POST, instance=ativo)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "arquivo.ativo"
        l.objeto_id = registro.id
        l.objeto_str = registro.id
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Ativo <b>' + registro.id + '</b> alterado')
        return redirect('arquivo_ativo_id', id)
    else:
        return render(request,'arquivo/ativo_id.html',{'form':form,'ativo':ativo})


# Metodos DELETE
@login_required
@permission_required('arquivo.delete_grupo', login_url="/handler/403")
def grupo_delete(request,id):
    try:
        registro = Grupo.objects.get(pk=id)
        l = Log()
        l.modelo = "arquivo.grupo"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Grupo <b>{registro.nome}</b> apagado. Essa operação não pode ser desfeita')
        return redirect('arquivo_grupos')
    except:
        messages.error(request,'ERRO ao apagar grupo')
        return redirect('arquivo_grupo_id', id)

@login_required
@permission_required('arquivo.delete_container', login_url="/handler/403")
def container_delete(request,id):
    try:
        registro = Container.objects.get(pk=id)
        l = Log()
        l.modelo = "arquivo.container"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Container <b>{registro.nome}</b> apagado. Essa operação não pode ser desfeita')
        return redirect('arquivo_containers')
    except:
        messages.error(request,'ERRO ao apagar container')
        return redirect('arquivo_container_id', id)

@login_required
@permission_required('arquivo.delete_limite', login_url="/handler/403")
def limite_delete(request,id):
    try:
        registro = Container.objects.get(pk=id)
        l = Log()
        l.modelo = "arquivo.limite"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Container <b>{registro.nome}</b> apagado. Essa operação não pode ser desfeita')
        return redirect('arquivo_limites')
    except:
        messages.error(request,'ERRO ao apagar limite')
        return redirect('arquivo_limite_id', id)

@login_required
@permission_required('arquivo.delete_ativo', login_url="/handler/403")
def ativo_delete(request,id):
    try:
        registro = Ativo.objects.get(pk=id)
        l = Log()
        l.modelo = "arquivo.ativo"
        l.objeto_id = registro.id
        l.objeto_str = registro.id
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Ativo <b>{registro.id}</b> apagado. Essa operação não pode ser desfeita')
        return redirect('arquivo_ativos')
    except:
        messages.error(request,'ERRO ao apagar ativo')
        return redirect('arquivo_ativo_id', id)

# Metodos AJAX
@login_required
def get_containers(request):
    containers = Container.objects.filter(inativo=False).order_by('nome')
    itens = []
    for item in containers:
        item_dict = vars(item) # Converte objeto em dicionario
        item_dict['ocupacao'] = item.ocupacao()
        if '_state' in item_dict: del item_dict['_state'] # Remove _state do dict (se existir)
        itens.append(item_dict)
    dataJSON = json_dumps(itens)
    return HttpResponse(dataJSON)

@login_required
def get_ativos(request):
    # Metodo retorna JSON ajustado para (integracao jsTable e component localidade)
    try:
        ativos = Ativo.objects.filter(chaves__contains=request.GET['pesquisa']).order_by('entrada')
        itens = []
        for item in ativos:
            item_dict = {
                '#':item.id,
                'Empresa':item.empresa.nome,
                'Setor': item.setor.nome,
                'Container': item.container.nome if item.container else '',
                'Grupo': item.grupo.nome,
                'Entrada': item.entrada.strftime("%d/%m/%Y"),
                'Vencimento': item.vencimento.strftime("%d/%m/%Y") if item.vencimento != '' else '',
                'Responsavel': item.responsavel,
                'Tipo': 'FISICO' if item.fisico else 'DIGITAL',
                'Status': item.get_status_display(),
            }
            if request.user.has_perm('arquivo.change_ativo'):
                item_dict['cnt'] = f'<a class="btn btn-sm btn-dark float-end" href="/arquivo_ativo_id/{item.id}"><i class="fas fa-pen"></i></a>'
            itens.append(item_dict)
        dataJSON = json_dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('[]')