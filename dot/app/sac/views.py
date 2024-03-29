from django.shortcuts import render, redirect
from django.http import HttpResponse
from json import dumps
from .models import Classificacao, Reclamacao, Settings
from .forms import ClassificacaoForm, ReclamacaoForm, SiteForm, SettingsForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from core.models import Log, Empresa
from django.conf import settings as ROOT


# METODOS SHOW
@login_required
@permission_required('sac.view_classificacao', login_url="/handler/403")
def classificacoes(request):
    classificacoes = Classificacao.objects.all().order_by('nome')
    return render(request, 'sac/classificacoes.html', {'classificacoes':classificacoes})

@login_required
@permission_required('sac.view_reclamacao', login_url="/handler/403")
def reclamacoes(request):
    reclamacoes = Reclamacao.objects.all().order_by('entrada')
    if request.GET.get('empresa', None):
        if request.GET['empresa'] != 'unassigned':
            empresa = Empresa.objects.get(id=request.GET['empresa'])
            reclamacoes = reclamacoes.filter(empresa=empresa)
            empresas = request.user.profile.empresas.all().exclude(id=empresa.id).order_by('nome')
        else:
            reclamacoes = reclamacoes.filter(empresa=None)
            empresas = request.user.profile.empresas.all().order_by('nome')
            empresa = None
    else:
        empresa = None
        empresas = request.user.profile.empresas.all().order_by('nome')
    if request.GET.get('de', None) and request.GET.get('ate', None):
        reclamacoes = reclamacoes.filter(data__range=(request.GET.get('de', None), request.GET.get('ate', None)))
    else:
        reclamacoes = reclamacoes.filter(tratado=False)
    try: # Carrega configuracoes do app
        settings = Settings.objects.all().get()
    except: # Caso nao gerado configuracoes iniciais carrega definicoes basicas
        settings = Settings()
    metrics = {
        'reclamacoes':reclamacoes,
        'prazo':settings.prazo_resposta,
        'empresa':empresa,
        'empresas':empresas
    }        
    return render(request, 'sac/reclamacoes.html', metrics)

@login_required
@permission_required('sac.view_settings', login_url="/handler/403")
def settings(request):
    try: # Busca configuracao do app
        settings = Settings.objects.all().get()
    except: # Caso ainda nao configurado, inicia com configuracao basica
        if Settings.objects.all().count() == 0:
            settings = Settings()
            settings.save()
            l = Log()
            l.modelo = "sac.settings"
            l.objeto_id = settings.id
            l.objeto_str = 'n/a'
            l.usuario = request.user
            l.mensagem = "AUTO CREATED"
            l.save()
            messages.warning(request,'<b>Informativo:</b> App configurado pela primeira vez.')
        else:
            settings = None
            messages.error(request,'<b>Erro::</b> Identificado duplicatas nas configurações do sistema, entre em contato com o administrador.')
    form = SettingsForm(instance=settings)
    return render(request,'sac/settings.html',{'form':form,'settings':settings})


def site(request):
    metrics = {'ROOT':ROOT.COMPANY_DATA}
    if request.method == 'POST':
        form = SiteForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save(commit=False)
                registro.origem = 'S'
                registro.usuario = request.user
                if registro.linha: # Para reclamacoes informado a linha, associa com respectiva empresa
                    registro.empresa = registro.linha.empresa
                    if registro.veiculo and registro.veiculo.empresa != registro.empresa: # Valida se carro informado eh da mesma empresa da linha informada, se nao descarta carro informado
                        registro.detalhe = f'Informado veiculo: {registro.veiculo.prefixo}, desconsiderado (n confere com empresa informada)\n---\n' + registro.detalhe
                        registro.veiculo = None
                else: # Caso nao informado a linha
                    if registro.veiculo: # Caso nao informado linha porem informado veiculo, assume a empresa do veiculo para reclamacao
                        registro.empresa = registro.veiculo.empresa
                registro.save()
                l = Log()
                l.modelo = "sac.reclamacao"
                l.objeto_id = registro.id
                l.objeto_str = registro.data.strftime("%d/%m/%y") + ' ' + registro.reclamante[0:20]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Reclamação registrada')
                metrics['status'] = 'SUCCESS'
            except:
                messages.error(request,'<b>Erro</b> ao registrar reclamação')
                metrics['status'] = 'ERROR'
        else:
            metrics['form'] = form
    return render(request,'sac/site.html', metrics)

# METODOS ADD
@login_required
@permission_required('sac.add_classificacao', login_url="/handler/403")
def classificacao_add(request):
    if request.method == 'POST':
        form = ClassificacaoForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "sac.classificacao"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Classificação <b>' + registro.nome + '</b> criada')
                return redirect('sac_classificacao_add')
            except:
                messages.error(request,'Erro ao inserir classificacao')
                return redirect('sac_classificacao_add')
    else:
        form = ClassificacaoForm()
    return render(request,'sac/classificacao_add.html',{'form':form})

@login_required
@permission_required('sac.add_reclamacao', login_url="/handler/403")
def reclamacao_add(request):
    if request.method == 'POST':
        form = ReclamacaoForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save(commit=False)
                registro.usuario = request.user
                registro.save()
                l = Log()
                l.modelo = "sac.reclamacao"
                l.objeto_id = registro.id
                l.objeto_str = registro.data.strftime("%d/%m/%y") + ' ' + registro.reclamante[0:20]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Reclamação <b>' + str(registro.id) + '</b> inserida')
                return redirect('sac_reclamacao_add')
            except:
                messages.error(request,'Erro ao inserir reclamação')
                return redirect('sac_reclamacao_add')
    else:
        form = ReclamacaoForm()
    return render(request,'sac/reclamacao_add.html',{'form':form})
    


# METODOS GET
@login_required
@permission_required('sac.change_classificacao', login_url="/handler/403")
def classificacao_id(request,id):
    classificacao = Classificacao.objects.get(pk=id)
    form = ClassificacaoForm(instance=classificacao)
    return render(request,'sac/classificacao_id.html',{'form':form,'classificacao':classificacao})

@login_required
@permission_required('sac.change_reclamacao', login_url="/handler/403")
def reclamacao_id(request,id):
    reclamacao = Reclamacao.objects.get(pk=id)
    form = ReclamacaoForm(instance=reclamacao)
    return render(request,'sac/reclamacao_id.html',{'form':form,'reclamacao':reclamacao})



# METODOS UPDATE
@login_required
@permission_required('sac.change_classificacao', login_url="/handler/403")
def classificacao_update(request,id):
    classificacao = Classificacao.objects.get(pk=id)
    form = ClassificacaoForm(request.POST, instance=classificacao)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "sac.classificacao"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Classificação <b>' + registro.nome + '</b> alterada')
        return redirect('sac_classificacao_id', id)
    else:
        return render(request,'sac/classificacao_id.html',{'form':form,'classificacao':classificacao})

@login_required
@permission_required('sac.change_reclamacao', login_url="/handler/403")
def reclamacao_update(request,id):
    reclamacao = Reclamacao.objects.get(pk=id)
    form = ReclamacaoForm(request.POST, instance=reclamacao)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "sac.reclamacao"
        l.objeto_id = registro.id
        l.objeto_str = registro.data.strftime("%d/%m/%y") + ' ' + registro.reclamante[0:20]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Reclamação <b>' + str(registro.id) + '</b> alterada')
        return redirect('sac_reclamacao_id', id)
    else:
        return render(request,'sac/reclamacao_id.html',{'form':form,'reclamacao':reclamacao})


@login_required
@permission_required('sac.change_settings', login_url="/handler/403")
def settings_update(request, id):
    settings = Settings.objects.get(pk=id)
    form = SettingsForm(request.POST, instance=settings)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "sac.settings"
        l.objeto_id = registro.id
        l.objeto_str = 'n/a'
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Settings <b>SAC</b> alterado')
        return redirect('sac_settings')
    else:
        return render(request,'sac/settings.html',{'form':form,'settings':settings})

# METODOS DELETE
@login_required
@permission_required('sac.delete_classificacao', login_url="/handler/403")
def classificacao_delete(request,id):
    try:
        registro = Classificacao.objects.get(pk=id)
        l = Log()
        l.modelo = "sac.classificacao"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Classificação <b>{registro.nome}</b> apagada. Essa operação não pode ser desfeita')
        return redirect('sac_classificacoes')
    except:
        messages.error(request,'ERRO ao apagar classificacao')
        return redirect('sac_classificacao_id', id)

@login_required
@permission_required('sac.delete_reclamacao', login_url="/handler/403")
def reclamacao_delete(request,id):
    try:
        registro = Reclamacao.objects.get(pk=id)
        l = Log()
        l.modelo = "sac.reclamacao"
        l.objeto_id = registro.id
        l.objeto_str = registro.data.strftime("%d/%m/%y") + ' ' + registro.reclamante[0:20]
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Reclamação apagada. Essa operação não pode ser desfeita')
        return redirect('sac_reclamacoes')
    except:
        messages.error(request,'ERRO ao apagar reclamação')
        return redirect('sac_reclamacao_id', id)


# METODOS AJAX
def get_classificacoes(request):
    try:
        classificacoes = Classificacao.objects.all().order_by('nome')
        if request.GET.get('tipo', None):
            classificacoes = classificacoes.filter(tipo=request.GET['tipo'])
        itens = {}
        for item in classificacoes:
            itens[item.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')