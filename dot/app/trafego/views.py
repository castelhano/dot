import os
import json
from json import dumps
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from core.models import Empresa, Log
from .models import Linha, Localidade, Trajeto, Patamar, Planejamento, Carro, Viagem, Evento, Providencia, Ocorrencia, FotoOcorrencia, Orgao, Agente, Enquadramento, Notificacao, Predefinido
from .forms import LinhaForm, LocalidadeForm, TrajetoForm, EventoForm, ProvidenciaForm, OcorrenciaForm, PlanejamentoForm, OrgaoForm, AgenteForm, EnquadramentoForm, NotificacaoForm, PredefinidoForm
from .validators import validate_file_extension
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from datetime import date, datetime


# METODOS SHOW
@login_required
@permission_required('trafego.view_localidade', login_url="/handler/403")
def localidades(request):
    if request.GET.get('showAll', None) == 'true':
        localidades = Localidade.objects.all().order_by('nome')
        return render(request,'trafego/localidades.html', {'localidades':localidades})
    return render(request,'trafego/localidades.html')

@login_required
@permission_required('trafego.view_linha', login_url="/handler/403")
def linhas(request):
    status = request.GET.get('status', 'A')
    linhas = Linha.objects.filter(status=status).order_by('codigo')
    if request.GET.get('empresa', None):
        try:
            empresa = request.user.profile.empresas.filter(id=request.GET.get('empresa', None)).get()
        except:
            messages.error(request,'Empresa <b>não encontrada</b> ou <b>não habilitada</b>')
            return redirect('trafego_linhas')
        linhas = linhas.filter(empresa=empresa)
        empresa_display = empresa.nome
    else:
        empresa_display = 'Todas'
        linhas = linhas.filter(empresa__in=request.user.profile.empresas.all())
    metrics = dict(status_display='Ativas' if status == 'A' else 'Inativas', empresa_display = empresa_display)
    return render(request,'trafego/linhas.html', {'linhas' : linhas, 'metrics':metrics})

@login_required
@permission_required('trafego.view_linha', login_url="/handler/403")
def trajetos(request, id_linha):
    metrics = {}
    if request.method == 'POST':
        form = TrajetoForm(request.POST)
        if form.is_valid():
            metrics['sentido'] = request.POST.get('sentido', None)
            try:
                registro = form.save(commit=False)
                if registro.seq == None:
                    registro.seq = Trajeto.objects.filter(linha=registro.linha, sentido=registro.sentido).count() + 1
                else:
                    # Caso informado sequencia que trajeto deva entrar, ajusta sequencias posteriores
                    qtde = Trajeto.objects.filter(linha=registro.linha, sentido=registro.sentido).count()
                    if registro.seq > qtde: # Caso informado sequencia maior que ponto existentes, ajusta para ultima sequencia
                        registro.seq = qtde + 1
                    for p in Trajeto.objects.filter(linha=registro.linha, sentido=registro.sentido, seq__gte=registro.seq):
                        p.seq += 1
                        p.save()
                registro.save()
                l = Log()
                l.modelo = "trafego.linha"
                l.objeto_id = registro.linha.id
                l.objeto_str = registro.linha.codigo
                l.usuario = request.user
                l.mensagem = "UPDATE"
                l.save()
            except Exception as e:
                messages.error(request,f'<b>Erro:</b> {e}')
        else:
            metrics['form'] = form
    try:
        metrics['linha'] = Linha.objects.get(id=id_linha)
        metrics['ida'] = Trajeto.objects.filter(linha=metrics['linha'], sentido='I').order_by('seq')
        metrics['volta'] = Trajeto.objects.filter(linha=metrics['linha'], sentido='V').order_by('seq')
        metrics['unico'] = Trajeto.objects.filter(linha=metrics['linha'], sentido='U').order_by('seq')
    except Exception as e:
        messages.error(request,f'<b>Erro:</b> {e}')
    return render(request, 'trafego/trajetos.html', metrics)

@login_required
@permission_required('trafego.view_planejamento', login_url="/handler/403")
def planejamentos(request):
    planejamentos = Planejamento.objects.all().order_by('linha__codigo', 'data_criacao')
    if request.GET.get('pesquisa', None):
        if Planejamento.objects.filter(codigo=request.GET['pesquisa']).exists():
            planejamento = Planejamento.objects.get(codigo=request.GET['pesquisa'])
            return redirect('trafego_planejamento_id', planejamento.id)
        else:
            planejamentos = planejamentos.filter(linha__codigo=request.GET['pesquisa'])
    else:
        planejamentos = planejamentos.filter(pin=True)
    return render(request,'trafego/planejamentos.html', {'planejamentos':planejamentos})

@login_required
@permission_required('trafego.view_evento', login_url="/handler/403")
def eventos(request):
    eventos = Evento.objects.all().order_by('nome')
    return render(request,'trafego/eventos.html',{'eventos':eventos})

@login_required
@permission_required('trafego.view_providencia', login_url="/handler/403")
def providencias(request):
    providencias = Providencia.objects.all().order_by('nome')
    return render(request,'trafego/providencias.html',{'providencias':providencias})

@login_required
@permission_required('trafego.view_ocorrencia', login_url="/handler/403")
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
            try:
                empresa = request.user.profile.empresas.filter(id=request.POST['empresa']).get()
            except:
                messages.error(request,'Empresa <b>não encontrada</b> ou <b>não habilitada</b>')
                return redirect('trafego_linhas')
            ocorrencias = ocorrencias.filter(empresa=empresa)
            empresa_display = empresa.nome
        else:
            empresa_display = 'Todas'
            ocorrencias = ocorrencias.filter(empresa__in=request.user.profile.empresas.all())
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
@permission_required('trafego.tratar_ocorrencia', login_url="/handler/403")
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

@login_required
@permission_required('trafego.view_predefinido', login_url="/handler/403")
def predefinidos(request):
    predefinidos = Predefinido.objects.all().order_by('abbr')
    return render(request, 'trafego/predefinidos.html', {'predefinidos':predefinidos})

@login_required
@permission_required('trafego.view_orgao', login_url="/handler/403")
def orgaos(request):
    orgaos = Orgao.objects.all().order_by('nome')
    return render(request, 'trafego/orgaos.html', {'orgaos':orgaos})

@login_required
@permission_required('trafego.view_agente', login_url="/handler/403")
def agentes(request):
    agentes = Agente.objects.all().order_by('nome')
    if request.GET.get('orgao', None):
        orgao = Orgao.objects.get(id=request.GET['orgao'])
        agentes = agentes.filter(orgao=orgao)
        orgao_display = orgao.nome
    else:
        orgao_display = 'Todos'
    return render(request, 'trafego/agentes.html', {'agentes':agentes, 'orgao_display':orgao_display})

@login_required
@permission_required('trafego.view_enquadramento', login_url="/handler/403")
def enquadramentos(request):
    enquadramentos = Enquadramento.objects.all().order_by('nome')
    return render(request, 'trafego/enquadramentos.html', {'enquadramentos':enquadramentos})

@login_required
@permission_required('trafego.view_notificacao', login_url="/handler/403")
def notificacoes(request):
    notificacoes = Notificacao.objects.all().order_by('data','hora')
    if request.method == 'POST':
        if request.POST['pesquisa'] != '':
            try:
                notificacao = Notificacao.objects.get(codigo=request.POST['pesquisa'])
                return redirect('trafego_notificacao_id', notificacao.id)
            except Exception as e:
                notificacoes = notificacoes.filter(Q(veiculo__prefixo=request.POST['pesquisa']) | Q(veiculo__placa__contains=request.POST['pesquisa']))
        if request.POST['orgao'] != '':
            notificacoes = notificacoes.filter(agente__orgao__id=request.POST['orgao'])
        if request.POST['tipo'] != '':
            notificacoes = notificacoes.filter(tipo=request.POST['tipo'])
        if request.POST['periodo_de'] != '' and request.POST['periodo_ate'] != '':
            notificacoes = notificacoes.filter(data__range=[request.POST['periodo_de'],request.POST['periodo_ate']])
        elif request.POST['pesquisa'] == '':
            notificacoes = notificacoes.filter(data=datetime.today())
    else:
        notificacoes = notificacoes.filter(data=datetime.today())
    return render(request, 'trafego/notificacoes.html', {'notificacoes':notificacoes})
        

# METODOS ADD
@login_required
@permission_required('trafego.add_localidade', login_url="/handler/403")
def localidade_add(request):
    if request.method == 'POST':
        form = LocalidadeForm(request.POST)
        if form.is_valid():
            try:
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
@permission_required('trafego.add_linha', login_url="/handler/403")
def linha_add(request):
    if request.method == 'POST':
        form = LinhaForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "trafego.linha"
                l.objeto_id = registro.id
                l.objeto_str = registro.codigo + ' - ' + registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Linha <b>{registro.codigo}</b> criada')
                return redirect('trafego_linha_id',registro.id)
            except:
                pass
    else:
        form = LinhaForm()
    return render(request,'trafego/linha_add.html',{'form':form})

@login_required
@permission_required('trafego.add_evento', login_url="/handler/403")
def evento_add(request):
    if request.method == 'POST':
        form = EventoForm(request.POST)
        if form.is_valid():
            try:
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
@permission_required('trafego.add_providencia', login_url="/handler/403")
def providencia_add(request):
    if request.method == 'POST':
        form = ProvidenciaForm(request.POST)
        if form.is_valid():
            try:
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
@permission_required('trafego.add_ocorrencia', login_url="/handler/403")
def ocorrencia_add(request):
    if request.method == 'POST':
        form = OcorrenciaForm(request.POST)
        if form.is_valid():
            try:
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
            except:
                messages.error(request,'Erro ao inserir ocorrencia')
                return redirect('trafego_ocorrencia_add')
    else:
        form = OcorrenciaForm()
    return render(request,'trafego/ocorrencia_add.html',{'form':form})

@login_required
@permission_required('trafego.add_planejamento', login_url="/handler/403")
def planejamento_add(request):
    if request.method == 'POST':
        form = PlanejamentoForm(request.POST, request.FILES)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.usuario = request.user
            registro.save()
            # Caso anexado planejamento (preformatado) insere viagens no planejamento
            if request.FILES.get('viagens', None):
                try:
                    viagens = json.load(request.FILES['viagens'])
                    viagens.sort(key=lambda x: x["carro"])
                except Exception as e:
                    messages.error(request,'<b>Erro</b> O arquivo anexado não é válido')
                    return render(request,'trafego/planejamento_id.html',{'form':form,'planejamento':planejamento})
                last_carro_seq = None
                carro = None
                for v in viagens:
                    if not last_carro_seq or last_carro_seq != v['carro']:
                        carro = Carro()
                        carro.planejamento = registro
                        carro.save()
                        last_carro_seq = v['carro']
                    v['carro'] = carro
                    try:
                        Viagem.objects.create(**v)
                    except Exception as e:
                        messages.error(request,f'<b>Erro</b>{e}, algumas viagens NÃO foram importadas')
                        return redirect('trafego_planejamento_add')
            # Se planejamento for marcado como ativo, inativa planejamento atual
            if registro.ativo:
                Planejamento.objects.filter(empresa=registro.empresa,linha=registro.linha,dia_tipo=registro.dia_tipo,ativo=True).exclude(id=registro.id).update(ativo=False)
            l = Log()
            l.modelo = "trafego.planejamento"
            l.objeto_id = registro.id
            l.objeto_str = registro.codigo
            l.usuario = request.user
            l.mensagem = "CREATED"
            l.save()
            messages.success(request,'Planejamento <b>' + registro.codigo + '</b> criado')
            return redirect('trafego_planejamento_id', registro.id)
    else:
        form = PlanejamentoForm()
    return render(request,'trafego/planejamento_add.html',{'form':form})

@login_required
@permission_required('trafego.add_predefinido', login_url="/handler/403")
def predefinido_add(request):
    if request.method == 'POST':
        form = PredefinidoForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "trafego.predefinido"
                l.objeto_id = registro.id
                l.objeto_str = registro.abbr[0:35]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Mensagem predefinida inserida')
                return redirect('trafego_predefinido_add')
            except:
                messages.error(request,'Erro ao inserir mensagem predefinida')
                return redirect('trafego_predefinido_add')
    else:
        form = PredefinidoForm()
    return render(request,'trafego/predefinido_add.html',{'form':form})

@login_required
@permission_required('trafego.add_orgao', login_url="/handler/403")
def orgao_add(request):
    if request.method == 'POST':
        form = OrgaoForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "trafego.orgao"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Orgao <b>' + registro.nome + '</b> criado')
                return redirect('trafego_orgao_add')
            except:
                messages.error(request,'Erro ao inserir orgao')
                return redirect('trafego_orgao_add')
    else:
        form = OrgaoForm()
    return render(request,'trafego/orgao_add.html',{'form':form})

@login_required
@permission_required('trafego.add_agente', login_url="/handler/403")
def agente_add(request):
    if request.method == 'POST':
        form = AgenteForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "trafego.agente"
                l.objeto_id = registro.id
                l.objeto_str = registro.matricula
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Agente <b>' + registro.matricula + '</b> cadastrado')
                return redirect('trafego_agente_add')
            except:
                messages.error(request,'Erro ao inserir agente')
                return redirect('trafego_agente_add')
    else:
        form = AgenteForm()
    return render(request,'trafego/agente_add.html',{'form':form})

@login_required
@permission_required('trafego.add_enquadramento', login_url="/handler/403")
def enquadramento_add(request):
    if request.method == 'POST':
        form = EnquadramentoForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "trafego.enquadramento"
                l.objeto_id = registro.id
                l.objeto_str = registro.codigo
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Enquadramento <b>' + registro.codigo + '</b> cadastrado')
                return redirect('trafego_enquadramento_add')
            except:
                messages.error(request,'Erro ao inserir enquadramento')
                return redirect('trafego_enquadramento_add')
    else:
        form = EnquadramentoForm()
    return render(request,'trafego/enquadramento_add.html',{'form':form})

@login_required
@permission_required('trafego.add_notificacao', login_url="/handler/403")
def notificacao_add(request):
    metrics = {
    'predefinidas':Predefinido.objects.all()
    }
    if request.method == 'POST':
        metrics['form'] = NotificacaoForm(request.POST)
        if metrics['form'].is_valid():
            try:
                registro = metrics['form'].save(commit=False)
                registro.create_by = request.user
                registro.save()
                l = Log()
                l.modelo = "trafego.notificacao"
                l.objeto_id = registro.id
                l.objeto_str = registro.codigo if registro.codigo else 'Nao Informado'
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Notificacao <b>' + l.objeto_str + '</b> inserida')
                return redirect('trafego_notificacao_add')
            except:
                messages.error(request,'Erro ao inserir notificacao')
                return redirect('trafego_notificacao_add')
    else:
        metrics['form'] = NotificacaoForm()
    return render(request,'trafego/notificacao_add.html', metrics)

# METODOS GET
@login_required
@permission_required('trafego.change_localidade', login_url="/handler/403")
def localidade_id(request, id):
    localidade = Localidade.objects.get(id=id)
    form = LocalidadeForm(instance=localidade)
    return render(request,'trafego/localidade_id.html',{'form':form,'localidade':localidade})

@login_required
@permission_required('trafego.view_linha', login_url="/handler/403")
def linha_id(request, id):
    linha = Linha.objects.get(id=id)
    form = LinhaForm(instance=linha)
    return render(request,'trafego/linha_id.html',{'form':form,'linha':linha})

@login_required
@permission_required('trafego.change_evento', login_url="/handler/403")
def evento_id(request,id):
    evento = Evento.objects.get(pk=id)
    form = EventoForm(instance=evento)
    return render(request,'trafego/evento_id.html',{'form':form,'evento':evento})

@login_required
@permission_required('trafego.change_providencia', login_url="/handler/403")
def providencia_id(request,id):
    providencia = Providencia.objects.get(pk=id)
    form = ProvidenciaForm(instance=providencia)
    return render(request,'trafego/providencia_id.html',{'form':form,'providencia':providencia})

@login_required
@permission_required('trafego.change_ocorrencia', login_url="/handler/403")
def ocorrencia_id(request,id):
    ocorrencia = Ocorrencia.objects.get(pk=id)
    if ocorrencia.usuario != request.user and not request.user.has_perm('trafego.tratar_ocorrencia'): 
        # SE USUARIO NAO FOR QUEM CRIOU OCORRENCIA, NEM TIVER LIBERACAO PARA TRATAR OCORRENCIA NÃO HABILITA EDICAO
        messages.warning(request,'Somente proprietario pode editar essa ocorrencia')
        return redirect('trafego_ocorrencias')
    form = OcorrenciaForm(instance=ocorrencia)
    return render(request,'trafego/ocorrencia_id.html',{'form':form,'ocorrencia':ocorrencia})

@login_required
@permission_required('trafego.tratar_ocorrencia', login_url="/handler/403")
def tratativa_id(request,id):
    ocorrencia = Ocorrencia.objects.get(pk=id)
    form = OcorrenciaForm(instance=ocorrencia)
    return render(request,'trafego/tratativa_id.html',{'form':form,'ocorrencia':ocorrencia})

@login_required
@permission_required('trafego.change_planejamento', login_url="/handler/403")
def planejamento_id(request,id):
    planejamento = Planejamento.objects.get(pk=id)
    if not planejamento.ativo:
        try:
            ativo = Planejamento.objects.filter(empresa=planejamento.empresa,linha=planejamento.linha,dia_tipo=planejamento.dia_tipo, ativo=True).get()             
        except:
            ativo = None
    else:
        ativo = None 
    form = PlanejamentoForm(instance=planejamento)
    return render(request,'trafego/planejamento_id.html',{'form':form,'planejamento':planejamento, 'ativo':ativo})

@login_required
@permission_required('trafego.view_planejamento', login_url="/handler/403")
def planejamento_horarios(request, id):
    planejamento = Planejamento.objects.get(pk=id)
    return render(request,'trafego/planejamento_horarios.html',{'planejamento':planejamento})

@login_required
@permission_required('trafego.change_predefinido', login_url="/handler/403")
def predefinido_id(request,id):
    predefinido = Predefinido.objects.get(pk=id)
    form = PredefinidoForm(instance=predefinido)
    return render(request,'trafego/predefinido_id.html',{'form':form,'predefinido':predefinido})

@login_required
@permission_required('trafego.change_orgao', login_url="/handler/403")
def orgao_id(request,id):
    orgao = Orgao.objects.get(pk=id)
    form = OrgaoForm(instance=orgao)
    return render(request,'trafego/orgao_id.html',{'form':form,'orgao':orgao})

@login_required
@permission_required('trafego.change_agente', login_url="/handler/403")
def agente_id(request,id):
    agente = Agente.objects.get(pk=id)
    form = AgenteForm(instance=agente)
    return render(request,'trafego/agente_id.html',{'form':form,'agente':agente})

@login_required
@permission_required('trafego.change_enquadramento', login_url="/handler/403")
def enquadramento_id(request,id):
    enquadramento = Enquadramento.objects.get(pk=id)
    form = EnquadramentoForm(instance=enquadramento)
    return render(request,'trafego/enquadramento_id.html',{'form':form,'enquadramento':enquadramento})

@login_required
@permission_required('trafego.change_notificacao', login_url="/handler/403")
def notificacao_id(request,id):
    notificacao = Notificacao.objects.get(pk=id)
    form = NotificacaoForm(instance=notificacao)
    predefinidas = Predefinido.objects.all()
    return render(request,'trafego/notificacao_id.html',{'form':form,'notificacao':notificacao,'predefinidas':predefinidas})

# METODOS UPDATE
@login_required
@permission_required('trafego.change_localidade', login_url="/handler/403")
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
@permission_required('trafego.change_linha', login_url="/handler/403")
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
@permission_required('trafego.change_linha', login_url="/handler/403")
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
@permission_required('trafego.change_patamar', login_url="/handler/403")
def patamar_update(request):
    # METODO PARA ADD E UPDATE DE PATAMARES
    if request.method == 'POST':
        try:
            linha = Linha.objects.get(id=request.POST['linha'])
            if request.POST['patamar'] != '':
                # PATAMAR EXISTENTE, CARREGA PARA UPDATE
                patamar = Patamar.objects.get(id=request.POST['patamar'])
            else:
                # NOVA INSERCAO
                patamar = Patamar()
                patamar.linha = linha
            patamar.inicial = int(request.POST['inicial'])
            patamar.final = int(request.POST['final'])
            patamar.ida = int(request.POST['ida'])
            patamar.volta = int(request.POST['volta'])
            has_errors = []
            has_errors.append(patamar.inicial > patamar.final)
            has_errors.append(patamar.inicial < 0 or patamar.final < 0)
            has_errors.append(patamar.inicial > 23 or patamar.final > 23)
            has_errors.append(patamar.ida < 1 or patamar.volta < 1)
            has_errors.append(patamar.ida > 540 or patamar.volta > 540) # INICIALMENTE CONSIDERADO VALOR MAXIMO PARA FAIXA DE 7 HORAS DE CICLO
            if True in has_errors:
                messages.error(request,f'<b>Erro: [PTC 1] Valores de patamar inválidos')
                return redirect('trafego_linha_id', linha.id)
            patamar.save()
                
            patamares = Patamar.objects.filter(linha=linha).exclude(id=patamar.id)
            retorno = patamar_tratar_conflitos(patamar, patamares)
            if retorno[0]:
                l = Log()
                l.modelo = "trafego.linha"
                l.objeto_id = linha.id
                l.objeto_str = linha.codigo + ' - ' + linha.nome
                l.usuario = request.user
                l.mensagem = "PATAMAR UPDATE"
                l.save()
                messages.success(request,'Patamares <b>atualizados</b>')
            else:
                messages.error(request,f'<b>Erro: [PTC 2]</b> {retorno[1]}')
        except Exception as e:
            messages.error(request,f'<b>Erro: [PTU 3]</b> {e}')
    return redirect('trafego_linha_id', linha.id)

def patamar_tratar_conflitos(patamar, patamares):
    try:
        for c in patamares:
            changed = False
            if c.inicial >= patamar.inicial and c.inicial <= patamar.final: # TRATA CONFLITO NO PERIODO INCIAL
                c.inicial = patamar.final + 1
                changed = True
            if c.final >= patamar.inicial and c.final <= patamar.final: # TRATA CONCLITO NO PERIODO FINAL
                c.final = patamar.inicial - 1
                changed = True
            if c.inicial <= patamar.inicial and c.final >= patamar.final:
            # TRATA CASO TODO INTERVALO ESTEJA CONFLITANDO, PODE RESULTAR EM DOIS PATAMARES COM OS INTERVALOS EXTERNOS AO NOVO PATAMAR
                n = Patamar()
                n.linha = c.linha
                n.inicial = patamar.final + 1
                n.final = c.final
                n.ida = c.ida
                n.volta = c.volta
                n.save()
                c.final = patamar.inicial - 1
                changed = True
            if changed:
                has_errors = []
                has_errors.append(c.inicial > c.final)
                has_errors.append(c.inicial < 0 or c.final < 0)
                has_errors.append(c.inicial > 23 or c.final > 23)
                if True in has_errors:
                    # VALIDA PATAMAR APOS AJUSTE DE CONFLITO, SE APRESENTAR RANGE INVALIDO (FAIXA NEGATIVA, APOS 23 HORAS, INICIAL MAIOR QUE FINAL, ETC) APAGA PATAMAR INVALIDO
                    c.delete()
                else:
                    # CASO CONTRARIO SALVA AJUSTES
                    c.save()
        return [True]
    except Exception as e:
        return [False, e]

@login_required
@permission_required('trafego.change_evento', login_url="/handler/403")
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
@permission_required('trafego.change_providencia', login_url="/handler/403")
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
@permission_required('trafego.change_ocorrencia', login_url="/handler/403")
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
@permission_required('trafego.tratar_ocorrencia', login_url="/handler/403")
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
@permission_required('trafego.tratar_ocorrencia', login_url="/handler/403")
def tratativa_marcar_todas_tratadas(request):
    resposta = Ocorrencia.objects.filter(tratado=False).update(tratado=True)
    messages.warning(request,f'Total de <b>{resposta}</b> ocorrencia(s) tratadas')
    return redirect('trafego_tratativas')

@login_required
@permission_required('trafego.change_planejamento', login_url="/handler/403")
def planejamento_update(request,id):
    planejamento = Planejamento.objects.get(pk=id)
    form = PlanejamentoForm(request.POST, request.FILES, instance=planejamento)
    if form.is_valid():
        registro = form.save()
        # Caso anexado planejamento (preformatado) sobrescreve viagens no planejamento
        if request.FILES.get('viagens', None):
            try:
                viagens = json.load(request.FILES['viagens'])
                viagens.sort(key=lambda x: x["carro"])
            except Exception as e:
                messages.error(request,'<b>Erro</b> O arquivo anexado não é válido')
                return render(request,'trafego/planejamento_id.html',{'form':form,'planejamento':planejamento})
            Carro.objects.filter(planejamento=registro).delete() # Limpa viagens atuais (caso exista)
            last_carro_seq = None
            carro = None
            for v in viagens:
                if not last_carro_seq or last_carro_seq != v['carro']:
                    carro = Carro()
                    carro.planejamento = registro
                    carro.save()
                    last_carro_seq = v['carro']
                v['carro'] = carro
                try:
                    Viagem.objects.create(**v)
                except Exception as e:
                    messages.error(request,f'<b>Erro</b>{e}, algumas viagens NÃO foram importadas')
                    return redirect('trafego_planejamento_id', planejamento.id)
        # Se planejamento for marcado como ativo, inativa planejamento atual
        try:
            if registro.ativo:
                Planejamento.objects.filter(empresa=registro.empresa,linha=registro.linha,dia_tipo=registro.dia_tipo,ativo=True).exclude(id=registro.id).update(ativo=False)
            l = Log()
            l.modelo = "trafego.planejamento"
            l.objeto_id = registro.id
            l.objeto_str = registro.codigo
            l.usuario = request.user
            l.mensagem = "UPDATE"
            l.save()
            messages.success(request,'Planejamento <b>' + registro.codigo + '</b> alterado')
            return redirect('trafego_planejamento_id', id)
        except Exception as e:
            messages.error(request,f'<b>Erro</b> ao concluir operação: {e}')
            return redirect('trafego_planejamento_id', planejamento.id)
    else:
        return render(request,'trafego/planejamento_id.html',{'form':form,'planejamento':planejamento})

@login_required
@permission_required('trafego.change_predefinido', login_url="/handler/403")
def predefinido_update(request,id):
    predefinido = Predefinido.objects.get(pk=id)
    form = PredefinidoForm(request.POST, instance=predefinido)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "trafego.predefinido"
        l.objeto_id = registro.id
        l.objeto_str = registro.abbr[0:35]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Mensagem predefinida alterada')
        return redirect('trafego_predefinido_id', id)
    else:
        return render(request,'trafego/predefinido_id.html',{'form':form,'predefinido':orgao})

@login_required
@permission_required('trafego.change_orgao', login_url="/handler/403")
def orgao_update(request,id):
    orgao = Orgao.objects.get(pk=id)
    form = OrgaoForm(request.POST, instance=orgao)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "trafego.orgao"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Orgao <b>' + registro.nome + '</b> alterado')
        return redirect('trafego_orgao_id', id)
    else:
        return render(request,'trafego/orgao_id.html',{'form':form,'orgao':orgao})

@login_required
@permission_required('trafego.change_agente', login_url="/handler/403")
def agente_update(request,id):
    agente = Agente.objects.get(pk=id)
    form = AgenteForm(request.POST, instance=agente)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "trafego.agente"
        l.objeto_id = registro.id
        l.objeto_str = registro.matricula
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Agente <b>' + registro.matricula + '</b> alterado')
        return redirect('trafego_agente_id', id)
    else:
        return render(request,'trafego/agente_id.html',{'form':form,'agente':agente})

@login_required
@permission_required('trafego.change_enquadramento', login_url="/handler/403")
def enquadramento_update(request,id):
    enquadramento = Enquadramento.objects.get(pk=id)
    form = EnquadramentoForm(request.POST, instance=enquadramento)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "trafego.enquadramento"
        l.objeto_id = registro.id
        l.objeto_str = registro.codigo
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Enquadramento <b>' + registro.codigo + '</b> alterado')
        return redirect('trafego_enquadramento_id', id)
    else:
        return render(request,'trafego/enquadramento_id.html',{'form':form,'enquadramento':enquadramento})

@login_required
@permission_required('trafego.change_notificacao', login_url="/handler/403")
def notificacao_update(request,id):
    notificacao = Notificacao.objects.get(pk=id)
    form = NotificacaoForm(request.POST, instance=notificacao)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "trafego.notificacao"
        l.objeto_id = registro.id
        l.objeto_str = registro.codigo if registro.codigo else 'Nao Informado'
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Notificacao <b>' + l.objeto_str + '</b> alterado')
        return redirect('trafego_notificacao_id', id)
    else:
        return render(request,'trafego/notificacao_id.html',{'form':form,'notificacao':notificacao})

# METODOS DELETE
@login_required
@permission_required('trafego.delete_localidade', login_url="/handler/403")
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
@permission_required('trafego.delete_linha', login_url="/handler/403")
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
@permission_required('trafego.change_linha', login_url="/handler/403")
def trajeto_delete(request, id):
    try:
        registro = Trajeto.objects.get(pk=id)
        l = Log()
        l.modelo = "trafego.linha"
        l.objeto_id = registro.linha.id
        l.objeto_str = registro.linha.codigo
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        registro.delete()
        for p in Trajeto.objects.filter(linha=registro.linha, sentido=registro.sentido, seq__gte=registro.seq):
            p.seq -= 1
            p.save()        
        return redirect('trafego_trajetos', registro.linha.id)
    except:
        messages.error(request,'<b>Erro</b> ao atualizar trajeto')
        return redirect('trafego_trajetos', registro.linha.id)

@login_required
@permission_required('trafego.delete_evento', login_url="/handler/403")
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
@permission_required('trafego.delete_providencia', login_url="/handler/403")
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
@permission_required('trafego.delete_ocorrencia', login_url="/handler/403")
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
@permission_required('trafego.delete_foto', login_url="/handler/403")
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

@login_required
@permission_required('trafego.delete_planejamento', login_url="/handler/403")
def planejamento_delete(request,id):
    try:
        registro = Planejamento.objects.get(pk=id)
        l = Log()
        l.modelo = "trafego.planejamento"
        l.objeto_id = registro.id
        l.objeto_str = registro.codigo
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Planejamento apagado. Essa operação não pode ser desfeita')
        return redirect('trafego_planejamentos')
    except:
        messages.error(request,'ERRO ao apagar planejamento')
        return redirect('trafego_planejamento_id', id)

@login_required
@permission_required('trafego.delete_predefinido', login_url="/handler/403")
def predefinido_delete(request,id):
    try:
        registro = Predefinido.objects.get(pk=id)
        l = Log()
        l.modelo = "trafego.predefinido"
        l.objeto_id = registro.id
        l.objeto_str = registro.abbr[0:35]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Mensagem predefinido apagada. Essa operação não pode ser desfeita')
        return redirect('trafego_predefinidos')
    except:
        messages.error(request,'ERRO ao apagar mensagem predefinida')
        return redirect('trafego_predefinido_id', id)

@login_required
@permission_required('trafego.delete_orgao', login_url="/handler/403")
def orgao_delete(request,id):
    try:
        registro = Orgao.objects.get(pk=id)
        l = Log()
        l.modelo = "trafego.orgao"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Orgao apagado. Essa operação não pode ser desfeita')
        return redirect('trafego_orgaos')
    except:
        messages.error(request,'ERRO ao apagar orgao')
        return redirect('trafego_orgao_id', id)

@login_required
@permission_required('trafego.delete_agente', login_url="/handler/403")
def agente_delete(request,id):
    try:
        registro = Agente.objects.get(pk=id)
        l = Log()
        l.modelo = "trafego.agente"
        l.objeto_id = registro.id
        l.objeto_str = registro.matricula
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Agente apagado. Essa operação não pode ser desfeita')
        return redirect('trafego_agentes')
    except:
        messages.error(request,'ERRO ao apagar agente')
        return redirect('trafego_agente_id', id)

@login_required
@permission_required('trafego.delete_enquadramento', login_url="/handler/403")
def enquadramento_delete(request,id):
    try:
        registro = Enquadramento.objects.get(pk=id)
        l = Log()
        l.modelo = "trafego.enquadramento"
        l.objeto_id = registro.id
        l.objeto_str = registro.codigo
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Enquadramento apagado. Essa operação não pode ser desfeita')
        return redirect('trafego_enquadramentos')
    except:
        messages.error(request,'ERRO ao apagar enquadramento')
        return redirect('trafego_enquadramento_id', id)

@login_required
@permission_required('trafego.delete_notificacao', login_url="/handler/403")
def notificacao_delete(request,id):
    try:
        registro = Notificacao.objects.get(pk=id)
        l = Log()
        l.modelo = "trafego.notificacao"
        l.objeto_id = registro.id
        l.objeto_str = registro.codigo if registro.codigo else 'Nao Informado'
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Notificacao apagada. Essa operação não pode ser desfeita')
        return redirect('trafego_notificacoes')
    except:
        messages.error(request,'ERRO ao apagar notificacao')
        return redirect('trafego_notificacao_id', id)

# METODOS AJAX
def get_linha(request):
    try:
        empresa = request.GET.get('empresa',None)
        codigo = request.GET.get('codigo',None)
        incluir_inativos = request.GET.get('incluir_inativos',None)
        multiempresa = request.GET.get('multiempresa', None)
        params  = dict(codigo=codigo)
        if not multiempresa or multiempresa != 'True':
            params['empresa__id'] = empresa
        linha = Linha.objects.get(**params)
        if incluir_inativos != 'True' and linha.status != 'A':
            raise Exception('')
        return HttpResponse(str(linha.id) + ';' + str(linha.nome) + ';' + str(linha.status) + ';' + str(linha.empresa.id))
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

def get_localidades(request):
    # Metodo retorna JSON ajustado para (integracao jsTable e component localidade)
    try:
        localidades = Localidade.objects.filter(nome__contains=request.GET['pesquisa']).order_by('nome')
        if request.GET.get('garagem', None) and request.GET['garagem'] == 'True':
            localidades = localidades.filter(eh_garagem=True)
        if request.GET.get('controle', None) and request.GET['controle'] == 'True':
            localidades = localidades.filter(ponto_de_controle=True)
        if request.GET.get('tturno', None) and request.GET['tturno'] == 'True':
            localidades = localidades.filter(troca_turno=True)
        itens = []
        for item in localidades:
            item_dict = {'#':item.id, 'Nome':item.nome, 'GAR': 'GAR' if item.eh_garagem else '', 'T Turno': 'T Turno' if item.troca_turno else '', 'Controle': 'Controle' if item.ponto_de_controle else ''}
            if request.user.has_perm('trafego.change_localidade'):
                item_dict['cnt'] = f'<a class="btn btn-sm btn-dark float-end" href="/trafego_localidade_id/{item.id}"><i class="fas fa-pen"></i></a>'
            itens.append(item_dict)
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

def get_enquadramentos(request):
    try:
        enquadramentos = Enquadramento.objects.filter(nome__contains=request.GET['pesquisa']).order_by('nome')
        itens = {}
        for item in enquadramentos:
            itens[item.nome] = item.id
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

def get_orgaos(request):
    try:
        orgaos = Orgao.objects.all().order_by('nome')
        itens = {}
        for item in orgaos:
            itens[item.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

def get_agente(request):
    try:
        matricula = request.GET.get('matricula',None)
        agente = Agente.objects.get(matricula=request.GET['matricula'])
        return HttpResponse(str(agente.id) + ';' + str(agente.nome) + ';' + str(agente.orgao.nome))
    except:
        return HttpResponse('')

@login_required
def get_ocorrencia(request):
    try:
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
    except:
        return HttpResponse('')