import os
import json
from json import dumps
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from .models import Linha, Localidade, Patamar, Carro, Viagem, Evento, Providencia, Ocorrencia, FotoOcorrencia
from core.models import Empresa
from .forms import LinhaForm, LocalidadeForm, EventoForm, ProvidenciaForm, OcorrenciaForm
from .validators import validate_file_extension
from core.models import Log
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from datetime import date


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
        if 'ponto_de_controle' in request.POST:
            localidades = localidades.filter(ponto_de_controle=True)
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

@login_required
@permission_required('trafego.view_evento')
def eventos(request):
    eventos = Evento.objects.all().order_by('nome')
    if request.method == 'POST':
        eventos = eventos.filter(nome__contains=request.POST['pesquisa'])
    return render(request,'trafego/eventos.html',{'eventos':eventos})

@login_required
@permission_required('trafego.view_providencia')
def providencias(request):
    providencias = Providencia.objects.all().order_by('nome')
    if request.method == 'POST':
        providencias = providencias.filter(nome__contains=request.POST['pesquisa'])
    return render(request,'trafego/providencias.html',{'providencias':providencias})

@login_required
@permission_required('trafego.view_ocorrencia')
def ocorrencias(request):
    ocorrencias = Ocorrencia.objects.all().order_by('data','hora')
    if request.method == 'POST':
        if request.POST['pesquisa']:
            ocorrencias = ocorrencias.filter(Q(veiculo__prefixo=request.POST['pesquisa']) | Q(linha__codigo=request.POST['pesquisa']) | Q(condutor__matricula=request.POST['pesquisa']))
        if request.POST['inicio'] != '' and request.POST['fim'] != '':
            ocorrencias = ocorrencias.filter(data__range=[request.POST['inicio'],request.POST['fim']]) 
        else:
            ocorrencias = ocorrencias.filter(data=date.today())            
        if request.POST['empresa'] != '':
            ocorrencias = ocorrencias.filter(empresa__id=request.POST['empresa'])
        if request.POST['evento'] != '':
            ocorrencias = ocorrencias.filter(evento__id=request.POST['evento'])
        if request.POST['gravidade'] != '':
            ocorrencias = ocorrencias.filter(gravidade=request.POST['gravidade'])        
        if 'indisciplina_condutor' in request.POST:
            ocorrencias = ocorrencias.filter(indisciplina_condutor=True)        
        if 'viagem_omitida' in request.POST:
            ocorrencias = ocorrencias.filter(viagem_omitida=True)        
    else:
        ocorrencias = ocorrencias.filter(data=date.today())
    return render(request,'trafego/ocorrencias.html',{'ocorrencias':ocorrencias})

@login_required
@permission_required('trafego.tratar_ocorrencia')
def tratativas(request):
    ocorrencias = Ocorrencia.objects.all().order_by('data','hora')
    if request.method == 'POST':
        validado = False
        if request.POST['pesquisa'] != '':
            ocorrencias = ocorrencias.filter(condutor__matricula=request.POST['pesquisa'])
            validado = True
        if request.POST['inicio'] != '' and request.POST['fim'] != '':
            ocorrencias = ocorrencias.filter(data__range=[request.POST['inicio'],request.POST['fim']])
            validado = True
        if request.POST['empresa'] != '':
            ocorrencias = ocorrencias.filter(empresa__id=request.POST['empresa'])
        if not 'tratado' in request.POST or not validado:
            ocorrencias = ocorrencias.filter(tratado=False)
        if 'indisciplina_condutor' in request.POST:
            ocorrencias = ocorrencias.filter(indisciplina_condutor=True)
        if not validado:
            messages.warning(request,'Informe uma matricula ou periodo para pesquisa')
            return redirect('trafego_tratativas')
    else:
        ocorrencias = ocorrencias.filter(tratado=False, indisciplina_condutor=True)
    return render(request,'trafego/tratativas.html',{'ocorrencias':ocorrencias})


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

@login_required
@permission_required('trafego.add_evento')
def evento_add(request):
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "trafego.evento"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Evento <b>' + registro.nome + '</b> criado')
                return redirect('trafego_evento_add')
            except:
                messages.error(request,'Erro ao inserir evento')
                return redirect('trafego_evento_add')
    else:
        form = EventoForm()
    return render(request,'trafego/evento_add.html',{'form':form})

@login_required
@permission_required('trafego.add_providencia')
def providencia_add(request):
    if request.method == 'POST':
        form = ProvidenciaForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "trafego.providencia"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Providencia <b>' + registro.nome + '</b> criada')
                return redirect('trafego_providencia_add')
            except:
                messages.error(request,'Erro ao inserir providencia')
                return redirect('trafego_providencia_add')
    else:
        form = ProvidenciaForm()
    return render(request,'trafego/providencia_add.html',{'form':form})

@login_required
@permission_required('trafego.add_ocorrencia')
def ocorrencia_add(request):
    if request.method == 'POST':
        form = OcorrenciaForm(request.POST)
        if form.is_valid():
            # try:
                form_clean = form.cleaned_data
                registro = form.save(commit=False)
                registro.usuario = request.user
                registro.save()
                l = Log()
                l.modelo = "trafego.ocorrencia"
                l.objeto_id = registro.id
                l.objeto_str = registro.evento.nome + registro.veiculo.prefixo if registro.veiculo != None else '' + ']'
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                for foto in request.FILES.getlist('fotos'):
                    if validate_file_extension(foto):
                        FotoOcorrencia.objects.create(ocorrencia=registro,foto=foto)
                messages.success(request,'Ocorrencia inserida')
                return redirect('trafego_ocorrencias')
            # except:
            #     messages.error(request,'Erro ao inserir ocorrencia')
            #     return redirect('trafego_ocorrencia_add')
    else:
        form = OcorrenciaForm()
    return render(request,'trafego/ocorrencia_add.html',{'form':form})

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

@login_required
@permission_required('trafego.change_evento')
def evento_id(request,id):
    evento = Evento.objects.get(pk=id)
    form = EventoForm(instance=evento)
    return render(request,'trafego/evento_id.html',{'form':form,'evento':evento})

@login_required
@permission_required('trafego.change_providencia')
def providencia_id(request,id):
    providencia = Providencia.objects.get(pk=id)
    form = ProvidenciaForm(instance=providencia)
    return render(request,'trafego/providencia_id.html',{'form':form,'providencia':providencia})

@login_required
@permission_required('trafego.change_ocorrencia')
def ocorrencia_id(request,id):
    ocorrencia = Ocorrencia.objects.get(pk=id)
    if ocorrencia.usuario != request.user and not request.user.has_perm('trafego.tratar_ocorrencia'): 
        # SE USUARIO NAO FOR QUEM CRIOU OCORRENCIA, NEM TIVER LIBERACAO PARA TRATAR OCORRENCIA NÃO HABILITA EDICAO
        messages.warning(request,'Somente proprietario pode editar essa ocorrencia')
        return redirect('trafego_ocorrencias')
    form = OcorrenciaForm(instance=ocorrencia)
    return render(request,'trafego/ocorrencia_id.html',{'form':form,'ocorrencia':ocorrencia})

@login_required
@permission_required('trafego.tratar_ocorrencia')
def tratativa_id(request,id):
    ocorrencia = Ocorrencia.objects.get(pk=id)
    form = OcorrenciaForm(instance=ocorrencia)
    return render(request,'trafego/tratativa_id.html',{'form':form,'ocorrencia':ocorrencia})


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

@login_required
@permission_required('trafego.change_evento')
def evento_update(request,id):
    evento = Evento.objects.get(pk=id)
    form = EventoForm(request.POST, instance=evento)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "trafego.evento"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Evento <b>' + registro.nome + '</b> alterado')
        return redirect('trafego_evento_id', id)
    else:
        return render(request,'trafego/evento_id.html',{'form':form,'evento':evento})

@login_required
@permission_required('trafego.change_providencia')
def providencia_update(request,id):
    providencia = Providencia.objects.get(pk=id)
    form = ProvidenciaForm(request.POST, instance=providencia)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "trafego.providencia"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Providencia <b>' + registro.nome + '</b> alterada')
        return redirect('trafego_providencia_id', id)
    else:
        return render(request,'trafego/providencia_id.html',{'form':form,'providencia':providencia})

@login_required
@permission_required('trafego.change_ocorrencia')
def ocorrencia_update(request,id):
    ocorrencia = Ocorrencia.objects.get(pk=id)
    if ocorrencia.usuario != request.user and not request.user.has_perm('trafego.tratar_ocorrencia'): 
        # SE USUARIO NAO FOR QUEM CRIOU OCORRENCIA, NEM TIVER LIBERACAO PARA TRATAR OCORRENCIA NÃO HABILITA EDICAO
        messages.warning(request,'Somente proprietario pode editar essa ocorrencia')
        return redirect('trafego_ocorrencias')
    form = OcorrenciaForm(request.POST, instance=ocorrencia)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "trafego.ocorrencia"
        l.objeto_id = registro.id
        l.objeto_str = registro.evento.nome + registro.veiculo.prefixo if registro.veiculo != None else '' + ']'
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        for foto in request.FILES.getlist('fotos'):
            if validate_file_extension(foto):
                FotoOcorrencia.objects.create(ocorrencia=registro,foto=foto)
        messages.success(request,'Ocorrencia alterada')
        return redirect('trafego_ocorrencia_id', id)
    else:
        return render(request,'trafego/ocorrencia_id.html',{'form':form,'ocorrencia':ocorrencia})

@login_required
@permission_required('trafego.tratar_ocorrencia')
def tratativa_update(request,id):
    if request.method == 'POST':
        ocorrencia = Ocorrencia.objects.get(pk=id)
        try:
            ocorrencia.providencia = Providencia.objects.get(id=request.POST['providencia'])
        except:
            messages.error(request,'É necessário informar a providencia')
            return redirect('trafego_tratativa_id', id)
        try:
            if 'tratado' in request.POST:
                ocorrencia.tratado = True
            else:
                ocorrencia.tratado = False
            ocorrencia.save()
            l = Log()
            l.modelo = "trafego.ocorrencia"
            l.objeto_id = ocorrencia.id
            l.objeto_str = ocorrencia.evento.nome + ocorrencia.veiculo.prefixo if ocorrencia.veiculo != None else '' + ']'
            l.usuario = request.user
            l.mensagem = "TRATADO"
            l.save()
            messages.success(request,'Ocorrencia tratada')
            return redirect('trafego_tratativas')
        except:
            messages.error(request,'Erro ao tratar ocorrencia')
            return redirect('trafego_tratativas')
    else:
        messages.warning(request,'Operação inválida')
        return redirect('trafego_tratativas')

@login_required
@permission_required('trafego.tratar_ocorrencia')
def tratativa_marcar_todas_tratadas(request,id):
    resposta = Ocorrencia.objects.filter(tratado=False).update(tratado=True)
    messages.warning(request,f'<b>{resposta[0]}</b> ocorrencias marcadas como tratadas')
    return redirect('trafego_tratativas')

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

@login_required
@permission_required('trafego.delete_evento')
def evento_delete(request,id):
    try:
        registro = Evento.objects.get(pk=id)
        l = Log()
        l.modelo = "trafego.evento"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Evento apagada. Essa operação não pode ser desfeita')
        return redirect('trafego_eventos')
    except:
        messages.error(request,'ERRO ao apagar evento')
        return redirect('trafego_evento_id', id)

@login_required
@permission_required('trafego.delete_providencia')
def providencia_delete(request,id):
    try:
        registro = Providencia.objects.get(pk=id)
        l = Log()
        l.modelo = "trafego.providencia"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Providencia apagada. Essa operação não pode ser desfeita')
        return redirect('trafego_providencias')
    except:
        messages.error(request,'ERRO ao apagar providencia')
        return redirect('trafego_providencia_id', id)

@login_required
@permission_required('trafego.delete_ocorrencia')
def ocorrencia_delete(request,id):
    try:
        registro = Ocorrencia.objects.get(pk=id)
        l = Log()
        l.modelo = "trafego.ocorrencia"
        l.objeto_id = registro.id
        l.objeto_str = registro.evento.nome + registro.veiculo.prefixo if registro.veiculo != None else '' + ']'
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Ocorrencia apagada. Essa operação não pode ser desfeita')
        return redirect('trafego_ocorrencias')
    except:
        messages.error(request,'ERRO ao apagar ocorrencia')
        return redirect('trafego_ocorrencia_id', id)

@login_required
@permission_required('trafego.delete_foto')
def foto_delete(request, id):
    registro = FotoOcorrencia.objects.get(pk=id)
    id_ocorrencia = registro.ocorrencia.id
    try:
        registro.delete()
        os.remove(registro.foto.path) # REMOVE ARQUIVO FISICO 
        messages.warning(request,'Foto apagada. Essa operação não pode ser desfeita')
        return redirect('trafego_ocorrencia_id', id_ocorrencia)
    except:
        messages.error(request,'ERRO ao apagar foto')
        return redirect('trafego_ocorrencia_id', id_ocorrencia)

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

def get_eventos(request):
    try:
        eventos = Evento.objects.all().order_by('nome')
        itens = {}
        for item in eventos:
            itens[item.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

@login_required
def get_ocorrencia(request):
    # try:
        id = request.GET.get('id_ocorrencia',None)
        ocorrencia = Ocorrencia.objects.get(id=id)
        ocorrencia_str = ocorrencia.data.strftime("%d/%m/%y") + ';' + ocorrencia.hora.strftime("%H:%M") + ';'
        ocorrencia_str += ocorrencia.evento.nome + ';' if ocorrencia.evento != None else ';'
        ocorrencia_str += str(ocorrencia.usuario.username) + ';'
        ocorrencia_str += str(ocorrencia.veiculo.prefixo) + ';' if ocorrencia.veiculo != None else ';'
        ocorrencia_str += str(ocorrencia.linha.codigo) + ' - ' + ocorrencia.linha.nome + ';' if ocorrencia.linha != None else ';'
        ocorrencia_str += str(ocorrencia.condutor.matricula) + ' - ' + ocorrencia.condutor.nome + ';' if ocorrencia.condutor != None else ';'
        ocorrencia_str += ocorrencia.detalhe
        return HttpResponse(ocorrencia_str)
    # except:
    #     return HttpResponse('')