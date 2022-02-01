import json
from json import dumps
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Linha, Localidade, Patamar, Carro, Viagem
from core.models import Empresa
from .forms import LinhaForm, LocalidadeForm
from core.models import Log
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages


# METODOS SHOW
@login_required
@permission_required('trafego.view_localidade')
def localidades(request):
    if request.method == 'POST':
        localidades = Localidade.objects.all().order_by('nome')
        if request.POST['pesquisa'] != '':
            localidades = localidades.filter(nome__contains=request.POST['pesquisa'])
        if 'eh_garagem' in request.POST:
            localidades = localidades.filter(eh_garagem=True)
        if 'troca_turno' in request.POST:
            localidades = localidades.filter(troca_turno=True)
    else:
        localidades = None
    return render(request,'trafego/localidades.html', {'localidades' : localidades})

@login_required
@permission_required('trafego.view_linha')
def linhas(request):
    status = request.GET.get('status', 'A')
    linhas = Linha.objects.filter(status=status).order_by('codigo')
    if request.GET.get('pesquisa', None):
        try:
            linha = Linha.objects.get(codigo=request.GET['pesquisa'])
            return redirect('trafego_linha_id', linha.id)
        except:
            linhas = linhas.filter(nome__contains=request.GET['pesquisa'])
    
    if request.GET.get('empresa', None) and request.GET['empresa'] != 'all':
        try:
            if request.user.is_superuser:
                empresa = Empresa.objects.get(id=request.GET.get('empresa', None))
            else:
                empresa = request.user.profile.empresas.filter(id=request.GET.get('empresa', None)).get()
        except:
            messages.error(request,'Empresa <b>não encontrada</b> ou <b>não habilitada</b>')
            return redirect('trafego_linhas')
        linhas = linhas.filter(empresa=empresa)
        empresa_display = empresa.nome
    else:
        empresa_display = 'Todas'
        if not request.user.is_superuser:
            linhas = linhas.filter(empresa__in=request.user.profile.empresas.all())
    metrics = dict(status_display='Ativas' if status == 'A' else 'Inativas', empresa_display = empresa_display)
    return render(request,'trafego/linhas.html', {'linhas' : linhas, 'metrics':metrics})

@login_required
@permission_required('trafego.view_patamar')
def patamares(request, id):
    linha = Linha.objects.get(pk=id)
    patamares = Patamar.objects.filter(linha=linha)
    return render(request,'trafego/patamares.html',{'linha':linha,'patamares':patamares})

@login_required
@permission_required('trafego.view_planejamento')
def planejamentos(request):
    return render(request,'trafego/planejamentos.html')

# METODOS ADD
@login_required
@permission_required('trafego.add_localidade')
def localidade_add(request):
    if request.method == 'POST':
        form = LocalidadeForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "trafego.localidade"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Localidade <b>{registro.nome}</b> criada')
                return redirect('trafego_localidade_add')
            except:
                pass
    else:
        form = LocalidadeForm()
    return render(request,'trafego/localidade_add.html',{'form':form})

@login_required
@permission_required('trafego.add_linha')
def linha_add(request):
    if request.method == 'POST':
        form = LinhaForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "trafego.linha"
                l.objeto_id = registro.id
                l.objeto_str = registro.codigo + ' - ' + registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                # CRIA OS PATAMARES BASE DE OPERACAO
                for faixa in range(24):
                    Patamar.objects.create(linha=registro,faixa=faixa,ida=50,volta=50)
                messages.success(request,f'Linha <b>{registro.codigo}</b> criada')
                return redirect('trafego_linha_id',registro.id)
            except:
                pass
    else:
        form = LinhaForm()
    return render(request,'trafego/linha_add.html',{'form':form})

# METODOS GET
@login_required
@permission_required('trafego.change_localidade')
def localidade_id(request, id):
    localidade = Localidade.objects.get(id=id)
    form = LocalidadeForm(instance=localidade)
    return render(request,'trafego/localidade_id.html',{'form':form,'localidade':localidade})

@login_required
@permission_required('trafego.view_linha')
def linha_id(request, id):
    linha = Linha.objects.get(id=id)
    form = LinhaForm(instance=linha)
    return render(request,'trafego/linha_id.html',{'form':form,'linha':linha})


# METODOS UPDATE
@login_required
@permission_required('trafego.change_localidade')
def localidade_update(request, id):
    localidade = Localidade.objects.get(pk=id)
    form = LocalidadeForm(request.POST, instance=localidade)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "trafego.localidade"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Localidade <b>{registro.nome}</b> alterada')
        return redirect('trafego_localidade_id', id)
    else:
        return render(request,'trafego/localidade_id.html',{'form':form,'localidade':localidade})

@login_required
@permission_required('trafego.change_linha')
def linha_update(request, id):
    linha = Linha.objects.get(pk=id)
    form = LinhaForm(request.POST, instance=linha)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "trafego.linha"
        l.objeto_id = registro.id
        l.objeto_str = registro.codigo[0:10] + ' - ' + registro.nome[0:38]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Linha <b>{registro.codigo}</b> alterada')
        return redirect('trafego_linha_id', id)
    else:
        return render(request,'trafego/linha_id.html',{'form':form,'linha':linha})

@login_required
@permission_required('trafego.change_linha')
def linha_movimentar(request, id):
    linha = Linha.objects.get(pk=id)
    status = request.GET.get('status', None)
    if status in ['A','I']:
        linha.status = status 
        linha.save()
        l = Log()
        l.modelo = "trafego.linha"
        l.objeto_id = linha.id
        l.objeto_str = linha.codigo[0:10] + ' - ' + linha.nome[0:38]
        l.usuario = request.user
        l.mensagem = "ATIVADA" if linha.status == 'A' else 'INATIVADA'
        l.save()
        messages.success(request,f'Linha <b>{linha.codigo}</b> {l.mensagem.lower()}')
    else:
        messages.warning(request,'Operação <b>inválida</b>')
    return redirect('trafego_linha_id', id)

@login_required
@permission_required('trafego.change_patamar')
def patamar_update(request):
    if request.method == 'POST':
        try:
            patamar = Patamar.objects.get(pk=request.POST['patamar'])
            sentido = request.POST['sentido']
            if sentido == 'I':
                patamar.ida = request.POST['ciclo']
            elif sentido == 'V':
                patamar.volta = request.POST['ciclo']
            else:
                messages.error(request,'Sentido invalido')
                return redirect('trafego_linha_id', patamar.id)
            patamar.save()
            
            if 'replicar' in request.POST:
                patamares = Patamar.objects.filter(linha=patamar.linha,faixa__gt=patamar.faixa)
                for patamar in patamares:
                    if sentido == 'I':
                        patamar.ida = request.POST['ciclo']
                    elif sentido == 'V':
                        patamar.volta = request.POST['ciclo']
                    patamar.save()
            l = Log()
            l.modelo = "trafego.linha"
            l.objeto_id = patamar.linha.id
            l.objeto_str = patamar.linha.codigo + ' - ' + patamar.linha.nome
            l.usuario = request.user
            l.mensagem = "PATAMAR UPDATE"
            l.save()
            messages.success(request,f'Patamares linha <b>{patamar.linha.codigo}</b> atualizados')
            return redirect('trafego_patamares', patamar.linha.id)
        except:
            messages.error(request,'<b>Erro</b> ao atualizar patamares')
            return redirect('index')        
    else:
        messages.error(request,'Operação inválida')
        return redirect('index')


# METODOS DELETE
@login_required
@permission_required('trafego.delete_localidade')
def localidade_delete(request, id):
    try:
        registro = Localidade.objects.get(pk=id)
        l = Log()
        l.modelo = "trafego.localidade"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Localidade apagada. Essa operação não pode ser desfeita')
        return redirect('trafego_localidades')
    except:
        messages.error(request,'<b>Erro</b> ao apagar localidade.')
        return redirect('trafego_localidade_id', id)

@login_required
@permission_required('trafego.delete_linha')
def linha_delete(request, id):
    try:
        registro = Linha.objects.get(pk=id)
        l = Log()
        l.modelo = "trafego.linha"
        l.objeto_id = registro.id
        l.objeto_str = registro.codigo + ' -  ' + registro.nome[0:38]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Linha apagada. Essa operação não pode ser desfeita')
        return redirect('trafego_linhas')
    except:
        messages.error(request,'<b>Erro</b> ao apagar linha')
        return redirect('trafego_linha_id', id)

# METODOS AJAX
def get_linha(request):
    try:
        empresa = request.GET.get('empresa',None)
        codigo = request.GET.get('codigo',None)
        incluir_inativos = request.GET.get('incluir_inativos',None)
        linha = Linha.objects.get(empresa__id=empresa,codigo=codigo)
        if incluir_inativos != 'True' and linha.status != 'A':
            raise Exception('')
        return HttpResponse(str(linha.id) + ';' + str(linha.nome) + ';' + str(linha.status))
    except:
        return HttpResponse('')

def get_linhas_empresa(request):
    try:
        empresa_id = request.GET.get('empresa',None)
        linhas = Linha.objects.filter(empresa__id=empresa_id,status='A').order_by('codigo')
        itens = {}
        for item in linhas:
            itens[item.codigo] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')