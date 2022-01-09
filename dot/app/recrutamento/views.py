from django.shortcuts import render, redirect
# from django.http import HttpResponse
# from json import dumps
from .models import Candidato, Selecao, Avaliacao, Vaga, Criterio
from pessoal.models import Cargo
from .forms import CandidatoForm, SelecaoForm, VagaForm, CriterioForm
from pessoal.validators import cpf_valid
from core.models import Log
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
# from datetime import datetime, date


# METODOS SHOW
@login_required
@permission_required('recrutamento.view_candidato')
def candidatos(request):
    candidatos = Candidato.objects.all().order_by('nome')
    if request.method == 'POST':
        if request.POST['pesquisa'] != '':
            candidatos = candidatos.filter(Q(nome__contains=request.POST['pesquisa']) | Q(cpf__contains=request.POST['pesquisa']))
        if request.POST['cargo'] != '':
            candidatos = candidatos.filter(vagas__id=request.POST['cargo'])
        if request.POST['status'] != '':
            candidatos = candidatos.filter(status=request.POST['status'])
        if request.POST['origem'] != '':
            candidatos = candidatos.filter(origem=request.POST['origem'])
        return render(request,'recrutamento/candidatos.html',{'candidatos':candidatos})
    else:
        nova_mensagem = Candidato.objects.filter(nova_mensagem=True).count()
        banco = Candidato.objects.filter(status='B').count()
        selecoes = Candidato.objects.filter(status='S').count()
        return render(request,'recrutamento/candidatos.html',{'banco':banco,'nova_mensagem':nova_mensagem,'selecoes':selecoes})

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
    if request.method == 'POST':
        if request.POST['pesquisa'] != '':
            vagas = vagas.filter(cargo__nome__contains=request.POST['pesquisa'])
        if 'abertas' in request.POST:
            vagas = vagas.filter(quantidade__gt=0)
    return render(request,'recrutamento/vagas.html',{'vagas':vagas})

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
                messages.success(request,f'Candidato {registro.nome.split(" ")[0]} criado')
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
                if Selecao.objects.filter(candidato=registro.candidato.id, vaga=registro.vaga.id, arquivar=False).exists():
                    messages.warning(request,'Canditado já esta participando de seleção para esta vaga')
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
                messages.success(request,'Seleção criada')
                return redirect('recrutamento_selecao_id',registro.id)
            except:
                messages.error(request,'Erro ao inserir selecao')
                return redirect('recrutamento_selecoes')
    else:
        form = SelecaoForm()
    return render(request,'recrutamento/selecao_add.html',{'form':form})
    
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
                Avaliacao.objects.create(selecao=selecao,criterio=Criterio.objects.get(id=request.POST['nome']),status=request.POST['status'])
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
        messages.success(request,f'Candidato {registro.nome.split(" ")[0]} alterado(a)')
        return redirect('recrutamento_candidato_id', id)
    else:
        return render(request,'recrutamento/candidato_id.html',{'form':form,'candidato':candidato})


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
        candidato = Candidato.objects.get(pk=registro.candidato.id)
        if request.POST['bloqueado_ate'] != '' and request.POST['resultado'] == 'R':
            candidato.bloqueado_ate = request.POST['bloqueado_ate']
            candidato.status = 'B'
        candidato.save()
        messages.success(request,'Selecao alterada')
        return redirect('recrutamento_selecao_id', id)
    else:
        messages.error(request,'Erro ao atualizar seleção')
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
        return render(request,'recrutamento/vaga.html',{'form':form,'vaga':vaga})
    
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
        l.save()
        registro.delete()
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
        l.save()
        registro.delete()
        messages.warning(request,'Selecao apagada. Essa operação não pode ser desfeita')
        return redirect('recrutamento_selecoes')
    except:
        messages.error(request,'ERRO ao apagar selecao')
        return redirect('recrutamento_selecao_id', id)

@login_required
@permission_required('recrutamento.delete_avaliacao')
def avaliacao_delete(request, id):
    selecao_id = request.GET['selecao_id']
    try:
        registro = Avaliacao.objects.get(id=id).delete()
        return redirect('recrutamento_selecao_id',selecao_id)
    except:
        messages.error(request,'ERRO ao apagar avaliacao')
        return redirect('recrutamento_selecao_id',selecao_id)

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
        l.save()
        registro.delete()
        messages.warning(request,'Vaga removida')
        return redirect('recrutamento_vagas')
    except:
        messages.error(request,'ERRO ao apagar vaga')
        return redirect('recrutamento_vaga_id', id)


# OUTROS METODOS
def get_vagas(request):
    try:
        vagas = Vaga.objects.all()
        ocultos = request.GET.get('ocultos',None)
        if ocultos != 'True':
            vagas = vagas.filter(visivel=True)
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