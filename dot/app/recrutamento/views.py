from django.shortcuts import render, redirect
from django.http import HttpResponse
from json import dumps
from .models import Candidato, Selecao, Avaliacao, Vaga, Criterio, Settings
from .forms import CandidatoForm, SelecaoForm, VagaForm, CriterioForm, SettingsForm
from pessoal.forms import FuncionarioForm
from core.models import Log
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
from core.extras import clean_request
from datetime import date

# METODOS SHOW
@login_required
@permission_required('recrutamento.view_candidato')
def candidatos(request):
    candidatos = Candidato.objects.all().order_by('nome')
    if request.method == 'POST':
        valid = False
        if request.POST['pesquisa'] != '' and len(request.POST['pesquisa']) > 3:
            valid = True
            candidatos = candidatos.filter(Q(nome__contains=request.POST['pesquisa']) | Q(cpf__contains=request.POST['pesquisa']))
        if request.POST['cargo'] != '':
            valid = True
            candidatos = candidatos.filter(vagas__id=request.POST['cargo'])
        if request.POST['status'] != '':
            candidatos = candidatos.filter(status=request.POST['status'])
        if request.POST['origem'] != '':
            candidatos = candidatos.filter(origem=request.POST['origem'])
        if 'pne' in request.POST:
            candidatos = candidatos.filter(pne=True)
        if not 'bloqueados' in request.POST:
            candidatos = candidatos.exclude(bloqueado_ate__gte=date.today())
        if 'global' in request.POST:
            valid = True
        if not valid:
            candidatos = None
        return render(request,'recrutamento/candidatos.html',{'candidatos':candidatos})
    else:
        summary = {}
        summary['banco'] = Candidato.objects.filter(status='B').count()
        summary['selecoes'] = Candidato.objects.filter(status='S').count()
        return render(request,'recrutamento/candidatos.html',{'summary':summary})

@login_required
@permission_required('recrutamento.view_selecao')
def selecoes(request):
    selecoes = Selecao.objects.all().order_by('data','candidato')
    if request.method == 'POST':
        if request.POST['pesquisa'] != '':
            selecoes = selecoes.filter(candidato__nome__contains=request.POST['pesquisa'])
        if request.POST['cargo'] != '':
            selecoes = selecoes.filter(vaga__id=request.POST['cargo'])
        if request.POST['resultado'] != '':
            selecoes = selecoes.filter(resultado=request.POST['resultado'])
    else:
        if request.GET.get('candidato',None):
            selecoes = selecoes.filter(candidato__id=request.GET['candidato'])
        else:
            selecoes = selecoes.filter(arquivar=False)
    return render(request,'recrutamento/selecoes.html',{'selecoes':selecoes})

@login_required
@permission_required('recrutamento.view_vaga')
def vagas(request):
    vagas = Vaga.objects.all()
    if request.GET.get('pesquisa', None):
        vagas = vagas.filter(cargo__nome__contains=request.GET.get('pesquisa'))
    fields = ['visivel','quantidade__gt']
    try:
        params = clean_request(request.GET, fields)
        vagas = vagas.filter(**params)
    except:
        messages.warning(request,'<b class="text-danger">Erro</b> ao filtrar vagas..')
        return redirect('recrutamento_vagas')
    return render(request,'recrutamento/vagas.html',{'vagas':vagas})

@login_required
@permission_required('recrutamento.view_criterio')
def criterios(request):
    criterios = Criterio.objects.all()
    if request.method == 'POST':
        criterios = criterios.filter(nome__contains=request.POST['pesquisa'])
    return render(request,'recrutamento/criterios.html',{'criterios':criterios})

@login_required
@permission_required('recrutamento.view_settings')
def settings(request):
    try: # Busca configuracao do app
        settings = Settings.objects.all().get()
    except: # Caso ainda nao configurado, inicia com configuracao basica
        if Settings.objects.all().count() == 0:
            settings = Settings()
            settings.save()
            l = Log()
            l.modelo = "recrutamento.settings"
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
    return render(request,'recrutamento/settings.html',{'form':form,'settings':settings})


def cadastro_site(request):
    if request.method == 'POST':
        form = CandidatoForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                registro.origem = 'S'
                registro.save()
                l = Log()
                l.modelo = "recrutamento.candidato"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = None
                l.mensagem = "CREATED AT SITE"
                l.save()
                messages.success(request, 'Cadastro realizado com sucesso')
                return render(request, 'recrutamento/site.html',{'status':'CREATED'})
            except:
                messages.error(request,'Erro ao cadastrar candidato')
                return redirect('recrutamento_candidato_add')
        vagas = None
    else:
        form = CandidatoForm()
        vagas = Vaga.objects.filter(visivel=True, quantidade__gt=0)
    return render(request, 'recrutamento/site.html', {'form':form, 'vagas':vagas})



# METODOS ADD
@login_required
@permission_required('recrutamento.add_candidato')
def candidato_add(request):
    if request.method == 'POST':
        form = CandidatoForm(request.POST,request.FILES)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "recrutamento.candidato"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Candidato <b>{registro.nome.split(" ")[0]}</b> inserido no banco')
                return redirect('recrutamento_candidato_id',registro.id)
            except:
                messages.error(request,'Erro ao cadastrar candidato')
                return redirect('recrutamento_candidato_add')
    else:
        form = CandidatoForm()
    return render(request,'recrutamento/candidato_add.html',{'form':form})

@login_required
@permission_required('recrutamento.add_selecao')
def selecao_add(request):
    if request.method == 'POST':
        form = SelecaoForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save(commit=False)
                if registro.candidato.status != 'B' or Selecao.objects.filter(candidato=registro.candidato.id, vaga=registro.vaga.id, resultado='').exists():
                    messages.warning(request,'Canditado precisa estar no banco e não pode ter outros processos seletivos em aberto')
                    return redirect('recrutamento_selecoes')
                registro.save()
                l = Log()
                l.modelo = "recrutamento.selecao"
                l.objeto_id = registro.id
                l.objeto_str = registro.candidato.nome + ' ' + registro.vaga.cargo.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                candidato = registro.candidato
                candidato.status = 'S'
                candidato.save()
                messages.success(request, f'Seleção iniciada para candidato <b>{registro.candidato.nome.split(" ")[0]}</b>')
                return redirect('recrutamento_selecao_id',registro.id)
            except:
                messages.error(request,'Erro ao inserir seleção')
                return redirect('recrutamento_selecoes')
    else:
        try:
            candidato = Candidato.objects.get(id=request.GET.get('candidato', None))
        except:
            messages.error(request,'Candidato não localizado')
            return redirect('recrutamento_candidatos')
        form = SelecaoForm(instance=candidato)
    return render(request,'recrutamento/selecao_add.html',{'form':form, 'candidato':candidato})
    
@login_required
@permission_required('recrutamento.add_avaliacao')
def avaliacao_add(request, selecao_id):
    if request.method == 'POST':
        try:
            if Avaliacao.objects.filter(selecao=selecao_id, criterio__id=request.POST['criterio']).exists():
                avaliacao = Avaliacao.objects.filter(selecao=selecao_id, criterio__id=request.POST['criterio']).get()
                avaliacao.status = request.POST['status']
                avaliacao.save()
            else:
                selecao = Selecao.objects.get(pk=selecao_id)
                Avaliacao.objects.create(selecao=selecao,criterio=Criterio.objects.get(id=request.POST['criterio']), status=request.POST['status'])
            return redirect('recrutamento_selecao_id',selecao_id)
        except:
            messages.error(request,'Erro ao inserir avaliação')
            return redirect('recrutamento_vagas')
    return redirect('recrutamento_selecao_id',selecao_id)

@login_required
@permission_required('recrutamento.add_vaga')
def vaga_add(request):
    if request.method == 'POST':
        form = VagaForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save(commit=False)
                if Vaga.objects.filter(cargo=registro.cargo).exists():
                    messages.warning(request,'Já existe vaga registrada para este cargo')
                    return redirect('recrutamento_vagas')
                registro.save()
                l = Log()
                l.modelo = "recrutamento.vaga"
                l.objeto_id = registro.id
                l.objeto_str = registro.cargo.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Vaga criada')
                return redirect('recrutamento_vagas')
            except:
                pass
    else:
        form = VagaForm()
    return render(request,'recrutamento/vaga_add.html',{'form':form})

@login_required
@permission_required('recrutamento.add_criterio')
def criterio_add(request):
    if request.method == 'POST':
        form = CriterioForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "recrutamento.criterio"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Criterio <b>{registro.nome}</b> criado')
                return redirect('recrutamento_criterio_add')
            except:
                pass
    else:
        form = CriterioForm()
    return render(request,'recrutamento/criterio_add.html',{'form':form})
    

# METODOS GET
@login_required
@permission_required('recrutamento.change_candidato')
def candidato_id(request, id):
    candidato = Candidato.objects.get(id=id)
    form = CandidatoForm(instance=candidato)
    return render(request,'recrutamento/candidato_id.html',{'form':form,'candidato':candidato})

@login_required
@permission_required('recrutamento.change_selecao')
def selecao_id(request, id):
    selecao = Selecao.objects.get(id=id)
    form = SelecaoForm(instance=selecao)
    return render(request,'recrutamento/selecao_id.html',{'form':form,'selecao':selecao})

@login_required
@permission_required('recrutamento.change_vaga')
def vaga_id(request, id):
    vaga = Vaga.objects.get(id=id)
    form = VagaForm(instance=vaga)
    return render(request,'recrutamento/vaga_id.html',{'form':form,'vaga':vaga})

@login_required
@permission_required('recrutamento.change_criterio')
def criterio_id(request, id):
    criterio = Criterio.objects.get(id=id)
    form = CriterioForm(instance=criterio)
    return render(request,'recrutamento/criterio_id.html',{'form':form,'criterio':criterio})
    

# METODOS UPDATE
@login_required
@permission_required('recrutamento.change_candidato')
def candidato_update(request, id):
    candidato = Candidato.objects.get(pk=id)
    form = CandidatoForm(request.POST, request.FILES, instance=candidato)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "recrutamento.candidato"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Candidato <b>{registro.nome.split(" ")[0]}</b> alterado(a)')
        return redirect('recrutamento_candidato_id', id)
    else:
        return render(request,'recrutamento/candidato_id.html',{'form':form,'candidato':candidato})

@login_required
@permission_required('recrutamento.change_candidato')
def candidato_movimentar(request, id):
    candidato = Candidato.objects.get(pk=id)
    try: # Carrega conficuracoes do app
        settings = Settings.objects.all().get()
    except: # Caso nao gerado configuracoes iniciais carrega definicoes basicas
        settings = Settings()
    l = Log()
    if request.GET.get('operacao', None) == 'descartar' and request.user.has_perm('recrutamento.descartar_candidato'):
        candidato.movimentar('D')
        l.mensagem = "DESCARTADO"
    elif request.GET.get('operacao', None) == 'contratar' and request.user.has_perm('recrutamento.contratar_candidato'):
        candidato.movimentar('C')
        l.mensagem = "CONTRATADO"
    elif request.GET.get('operacao', None) == 'retornar' and request.user.has_perm('recrutamento.descartar_candidato'):
        candidato.movimentar('B')
        l.mensagem = "RETORNADO BANCO"
    else:
        messages.error(request,'Operação não autorizada')
        return redirect('recrutamento_candidato_id', id)        
    candidato.save()
    l.modelo = "recrutamento.candidato"
    l.objeto_id = candidato.id
    l.objeto_str = candidato.nome[0:48]
    l.usuario = request.user
    l.save()
    messages.warning(request,f'Candidato <b>{candidato.nome.split(" ")[0]}</b> {l.mensagem.lower()}')
    if request.GET.get('operacao', None) == 'contratar' and settings.redirecinar_cadastro_ao_aprovar and request.user.has_perm('pessoal.add_funcionario'): # Precarrega form com dados do candidato e redireciona para tela de criação de funcionario
        form = FuncionarioForm(instance=candidato)
        return render(request, 'pessoal/funcionario_add.html', {'form':form})
    return redirect('recrutamento_candidato_id', id)

@login_required
@permission_required('recrutamento.change_selecao')
def selecao_update(request, id):
    selecao = Selecao.objects.get(pk=id)
    form = SelecaoForm(request.POST, instance=selecao)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "recrutamento.selecao"
        l.objeto_id = registro.id
        l.objeto_str = registro.candidato.nome + ' ' + registro.vaga.cargo.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Selecao alterada')
        return redirect('recrutamento_selecao_id', id)
    else:
        messages.error(request,'Erro ao atualizar seleção')
        return redirect('recrutamento_selecao_id', id)

@login_required
@permission_required('recrutamento.change_selecao')
def selecao_movimentar(request, id):
    selecao = Selecao.objects.get(pk=id)
    l = Log()
    mensagem = ''
    try: # Carrega conficuracoes do app
        settings = Settings.objects.all().get()
    except: # Caso nao gerado configuracoes iniciais carrega definicoes basicas
        settings = Settings()
    if request.GET.get('operacao', None) == 'aprovar':
        selecao.movimentar('A')
        l.mensagem = "APROVADO"
        mensagem = 'Seleção concluida como <b>aprovado</b>.'
    elif request.GET.get('operacao', None) == 'reprovar' and request.user.has_perm('recrutamento.change_candidato'):
        selecao.movimentar('R')
        l.mensagem = "REPROVADO"
        mensagem = 'Seleção concluida como <b>reprovado</b>'
        candidato = selecao.candidato
        if settings.descartar_reprovados:
            candidato.movimentar('D')
        else: 
            args = dict(dias_bloqueio=settings.dias_bloqueio)
            candidato.movimentar('B', **args)
        candidato.save()
    elif request.GET.get('operacao', None) == 'retornar' and request.user.has_perm('recrutamento.change_candidato'):
        selecao.movimentar('')
        l.mensagem = "RETORNADO"
        mensagem = 'Seleção <b>retornada</b>.'
        candidato = selecao.candidato
        candidato.movimentar('S')
        candidato.save()
    else:
        messages.error(request,'Operação não autorizada')
        return redirect('recrutamento_selecao_id', id)        
    selecao.save()
    l.modelo = "recrutamento.selecao"
    l.objeto_id = selecao.id
    l.objeto_str = selecao.candidato.nome[0:48]
    l.usuario = request.user
    l.save()
    messages.warning(request, mensagem)
    return redirect('recrutamento_selecao_id', id)

@login_required
@permission_required('recrutamento.change_vaga')
def vaga_update(request, id):
    vaga = Vaga.objects.get(pk=id)
    form = VagaForm(request.POST, instance=vaga)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "recrutamento.vaga"
        l.objeto_id = registro.id
        l.objeto_str = registro.cargo.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Vaga alterada')
        return redirect('recrutamento_vaga_id', id)
    else:
        return render(request,'recrutamento/vaga_id.html',{'form':form,'vaga':vaga})

@login_required
@permission_required('recrutamento.change_criterio')
def criterio_update(request, id):
    criterio = Criterio.objects.get(pk=id)
    form = CriterioForm(request.POST, instance=criterio)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "recrutamento.criterio"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Criterio <b>{registro.nome}</b> alterado')
        return redirect('recrutamento_criterio_id', id)
    else:
        return render(request,'recrutamento/criterio_id.html',{'form':form,'criterio':criterio})

@login_required
@permission_required('recrutamento.change_settings')
def settings_update(request, id):
    settings = Settings.objects.get(pk=id)
    form = SettingsForm(request.POST, instance=settings)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "recrutamento.settings"
        l.objeto_id = registro.id
        l.objeto_str = 'n/a'
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Settings <b>recrutamento</b> alterado')
        return redirect('recrutamento_settings')
    else:
        return render(request,'recrutamento/settings.html',{'form':form,'settings':settings})
    
# METODOS DELETE
@login_required
@permission_required('recrutamento.delete_candidato')
def candidato_delete(request, id):
    try:
        registro = Candidato.objects.get(id=id)
        l = Log()
        l.modelo = "recrutamento.candidato"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,'Candidato apagado. Essa operação não pode ser desfeita')
        return redirect('recrutamento_candidatos')
    except:
        messages.error(request,'ERRO ao apagar candidato')
        return redirect('recrutamento_candidato_id', id)

@login_required
@permission_required('recrutamento.delete_selecao')
def selecao_delete(request, id):
    try:
        registro = Selecao.objects.get(id=id)
        l = Log()
        l.modelo = "recrutamento.selecao"
        l.objeto_id = registro.id
        l.objeto_str = registro.candidato.nome + ' ' + registro.vaga.cargo.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,'Selecao apagada. Essa operação não pode ser desfeita')
        return redirect('recrutamento_selecoes')
    except:
        messages.error(request,'ERRO ao apagar selecao')
        return redirect('recrutamento_selecao_id', id)

@login_required
@permission_required('recrutamento.delete_avaliacao')
def avaliacao_delete(request, id):
    try:
        registro = Avaliacao.objects.get(id=id)
        registro.delete()
    except:
        messages.error(request,'ERRO ao apagar avaliacao')
    return redirect('recrutamento_selecao_id',registro.selecao.id)

@login_required
@permission_required('recrutamento.delete_vaga')
def vaga_delete(request, id):
    try:
        registro = Vaga.objects.get(id=id)
        l = Log()
        l.modelo = "recrutamento.vaga"
        l.objeto_id = registro.id
        l.objeto_str = registro.cargo.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,'Vaga removida')
        return redirect('recrutamento_vagas')
    except:
        messages.error(request,'ERRO ao apagar vaga')
        return redirect('recrutamento_vaga_id', id)

@login_required
@permission_required('recrutamento.delete_criterio')
def criterio_delete(request, id):
    try:
        registro = Criterio.objects.get(id=id)
        l = Log()
        l.modelo = "recrutamento.criterio"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Criterio <b>{registro.nome}</b> removido')
        return redirect('recrutamento_criterios')
    except:
        messages.error(request,'ERRO ao apagar criterio')
        return redirect('recrutamento_criterio_id', id)


# OUTROS METODOS
def get_vagas(request):
    try:
        vagas = Vaga.objects.all()
        ocultos = request.GET.get('ocultos',None)
        vazios = request.GET.get('vazios',None)
        if ocultos != 'True':
            vagas = vagas.filter(visivel=True)
        if not vazios or vazios != 'True':
            vagas = vagas.filter(quantidade__gt=0)
        itens = {}
        for item in vagas:
            itens[item.cargo.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

def get_cargos_banco(request):
    try:
        vagas = Vaga.objects.filter(candidatos__in=Candidato.objects.filter(status='B')).distinct().order_by('cargo__nome')
        itens = {}
        for item in vagas:
            itens[item.cargo.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

def get_criterios(request):
    try:
        criterios = Criterio.objects.all().order_by('nome')
        itens = {}
        for item in criterios:
            itens[item.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')