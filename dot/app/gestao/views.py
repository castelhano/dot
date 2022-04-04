# from django.http import HttpResponse
# from json import dumps
from django.shortcuts import render, redirect
from .models import Indicador, Apontamento, Staff, Diretriz, Label, Analise, Plano
from .forms import IndicadorForm, ApontamentoForm, StaffForm, DiretrizForm, LabelForm, AnaliseForm, PlanoForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth.models import User
from core.models import Log
from core.extras import clean_request
# from datetime import date


# METODOS SHOW
@login_required
@permission_required('gestao.dashboard')
def dashboard(request):
    try:
        staff = Staff.objects.get(usuario=request.user)
        diretrizes = Diretriz.objects.filter(ativo=True).order_by('created_on')
        return render(request,'gestao/dashboard.html',{'staff':staff,'diretrizes':diretrizes})
    except:
        messages.warning(request,'Seu usuário precisa fazer parte da <b>Staff</b> para acessar este recurso.')
        if request.user.has_perm('gestao.view_staff'):
            return redirect('gestao_staffs')
        else:
            return redirect('index')

@login_required
@permission_required('gestao.dashboard')
def indicadores(request):
    indicadores = Indicador.objects.all().order_by('nome')
    fields = ['ativo','evolucao']
    try:
        params = clean_request(request.GET, fields)
        indicadores = indicadores.filter(**params)
        return render(request,'gestao/indicadores.html', {'indicadores' : indicadores})
    except:
        messages.warning(request,'<b class="text-danger">Erro</b> ao filtrar indicadores')
        return redirect('gestao_indicadores')

@login_required
@permission_required('gestao.dashboard')
def apontamentos(request, indicador):
    apontamentos = Apontamento.objects.filter(indicador__id=indicador).order_by('referencia')
    return render(request,'gestao/apontamentos.html', {'apontamentos' : apontamentos})

@login_required
@permission_required('gestao.dashboard')
def staffs(request):
    staffs = Staff.objects.all().order_by('usuario__username')
    fields = ['role','usuario__is_active']
    try:
        params = clean_request(request.GET, fields)
        staffs = staffs.filter(**params)
        return render(request,'gestao/staffs.html', {'staffs' : staffs})
    except:
        messages.warning(request,'<b class="text-danger">Erro</b> ao filtrar staff')
        return redirect('gestao_staffs')

@login_required
@permission_required('gestao.dashboard')
def diretrizes(request):
    diretrizes = Diretriz.objects.all().order_by('indicador','created_on')
    if request.method == 'POST':
        pass
    else:
        diretrizes = diretrizes.filter(ativo=True)
    return render(request,'gestao/diretrizes.html', {'diretrizes' : diretrizes})

@login_required
@permission_required('gestao.dashboard')
def labels(request):
    labels = Label.objects.all().order_by('nome')
    if request.method == 'POST' and request.POST['pesquisa'] != '':
        labels = labels.filter(nome__contains=request.POST['pesquisa'])
    return render(request,'gestao/labels.html', {'labels' : labels})

@login_required
@permission_required('gestao.dashboard')
def analises(request):
    analises = Analise.objects.all().order_by('created_on')
    if request.method == 'POST' and request.POST['pesquisa'] != '':
        pass
    else:
        analises = analises.filter(concluido=False)        
    return render(request,'gestao/analises.html', {'analises' : analises})

# METODOS ADD
@login_required
@permission_required('gestao.dashboard')
def indicador_add(request):
    if request.method == 'POST':
        form = IndicadorForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "gestao.indicador"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Indicador <b>' + registro.nome + '</b> criado')
                return redirect('gestao_indicador_add')
            except:
                messages.error(request,'Erro ao inserir indicador')
                return redirect('gestao_indicador_add')
    else:
        form = IndicadorForm()
    return render(request,'gestao/indicador_add.html',{'form':form})

@login_required
@permission_required('gestao.dashboard')
def apontamento_add(request):
    if request.method == 'POST':
        form = ApontamentoForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save(commit=False)
                registro.referencia = f"{request.POST['ano']}_{request.POST['mes']}"
                registro.save()
                l = Log()
                l.modelo = "gestao.indicador"
                l.objeto_id = registro.indicador.id
                l.objeto_str = f'{registro.indicador.id}_{registro.referencia}'
                l.usuario = request.user
                l.mensagem = "APONTAMENTO ADD"
                l.save()
                messages.success(request,'Apontamento <b>inserido</b>')
                return redirect('gestao_apontamento_add')
            except:
                messages.error(request,'Erro ao inserir apontamento')
                return redirect('gestao_apontamento_add')
    else:
        form = ApontamentoForm()
    return render(request,'gestao/apontamento_add.html',{'form':form})

@login_required
@permission_required('gestao.dashboard')
def staff_add(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "gestao.staff"
                l.objeto_id = registro.id
                l.objeto_str = registro.usuario.username
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Staff <b>' + registro.usuario.username + '</b> criado')
                return redirect('gestao_staff_add')
            except:
                messages.error(request,'Erro ao inserir staff')
                return redirect('gestao_staff_add')
    else:
        form = StaffForm()
    return render(request,'gestao/staff_add.html',{'form':form})

@login_required
@permission_required('gestao.dashboard')
def diretriz_add(request):
    if request.method == 'POST':
        form = DiretrizForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save(commit=False)
                registro.created_by = request.user
                registro.save()
                l = Log()
                l.modelo = "gestao.diretriz"
                l.objeto_id = registro.id
                l.objeto_str = 'Nao aplicavel'
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Diretriz <b>' + str(registro.id) + '</b> criada')
                return redirect('gestao_diretriz_add')
            except:
                messages.error(request,'Erro ao inserir diretriz')
                return redirect('gestao_diretriz_add')
    else:
        form = DiretrizForm()
    return render(request,'gestao/diretriz_add.html',{'form':form})

@login_required
@permission_required('gestao.dashboard')
def label_add(request):
    if request.method == 'POST':
        form = LabelForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "gestao.label"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Label <b>' + registro.nome + '</b> criada')
                return redirect('gestao_label_add')
            except:
                messages.error(request,'Erro ao inserir label')
                return redirect('gestao_label_add')
    else:
        form = LabelForm()
    return render(request,'gestao/label_add.html',{'form':form})

@login_required
@permission_required('gestao.dashboard')
def analise_add(request):
    if request.method == 'POST':
        form = AnaliseForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "gestao.analise"
                l.objeto_id = registro.id
                l.objeto_str = 'Nao aplicavel'
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Analise <b>' + registro.id + '</b> inserida')
                return redirect('gestao_analise_add') # AQUI ESTA ERRADO !!!!
            except:
                messages.error(request,'Erro ao inserir analise')
                return redirect('gestao_analise_add')
    else:
        form = AnaliseForm()
    return render(request,'gestao/analise_add.html',{'form':form})

@login_required
@permission_required('gestao.dashboard')
def plano_add(request, diretriz):
    if request.method == 'POST':
        form = PlanoForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                registro.created_by = request.user
                registro.save()
                l = Log()
                l.modelo = "gestao.plano"
                l.objeto_id = registro.id
                l.objeto_str = registro.titulo[0:40]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Plano <b>criado</b>')
                return redirect('gestao_dashboard')
            except:
                messages.error(request,'Erro ao inserir plano')
                return redirect('gestao_dashboard')
        else:
            d = Diretriz.objects.get(id=diretriz)
            p = Plano()
            p.diretriz = d
    else:
        p = Plano()
        d = Diretriz.objects.get(id=diretriz)
        p.diretriz = d
        form = PlanoForm(instance=p)
    return render(request,'gestao/plano_add.html',{'form':form,'plano':p})

# METODOS GET
@login_required
@permission_required('gestao.dashboard')
def indicador_id(request,id):
    indicador = Indicador.objects.get(pk=id)
    form = IndicadorForm(instance=indicador)
    return render(request,'gestao/indicador_id.html',{'form':form,'indicador':indicador})

@login_required
@permission_required('gestao.dashboard')
def apontamento_id(request,id):
    apontamento = Apontamento.objects.get(pk=id)
    form = ApontamentoForm(instance=apontamento)
    return render(request,'gestao/apontamento_id.html',{'form':form,'apontamento':apontamento})

@login_required
@permission_required('gestao.dashboard')
def staff_id(request,id):
    staff = Staff.objects.get(pk=id)
    form = StaffForm(instance=staff)
    return render(request,'gestao/staff_id.html',{'form':form,'staff':staff})

@login_required
@permission_required('gestao.dashboard')
def diretriz_id(request,id):
    diretriz = Diretriz.objects.get(pk=id)
    form = DiretrizForm(instance=diretriz)
    return render(request,'gestao/diretriz_id.html',{'form':form,'diretriz':diretriz})

@login_required
@permission_required('gestao.dashboard')
def label_id(request,id):
    label = Label.objects.get(pk=id)
    form = LabelForm(instance=label)
    return render(request,'gestao/label_id.html',{'form':form,'label':label})

@login_required
@permission_required('gestao.dashboard')
def analise_id(request,id):
    analise = Analise.objects.get(pk=id)
    form = AnaliseForm(instance=analise)
    return render(request,'gestao/analise_id.html',{'form':form,'analise':analise})

@login_required
@permission_required('gestao.dashboard')
def plano_id(request,id):
    plano = Plano.objects.get(pk=id)
    form = PlanoForm(instance=plano)
    return render(request,'gestao/plano_id.html',{'form':form,'plano':plano})

# METODOS UPDATE
@login_required
@permission_required('gestao.dashboard')
def indicador_update(request,id):
    indicador = Indicador.objects.get(pk=id)
    form = IndicadorForm(request.POST, instance=indicador)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "gestao.indicador"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:30]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Indicador <b>' + registro.nome + '</b> alterado')
        return redirect('gestao_indicador_id', id)
    else:
        return render(request,'gestao/indicador_id.html',{'form':form,'indicador':indicador})

@login_required
@permission_required('gestao.dashboard')
def apontamento_update(request,id):
    apontamento = Apontamento.objects.get(pk=id)
    form = ApontamentoForm(request.POST, instance=apontamento)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "gestao.indicador"
        l.objeto_id = registro.indicador.id
        l.objeto_str = f'{registro.indicador.id}_{registro.referencia}'
        l.usuario = request.user
        l.mensagem = "APONTAMENTO UPDATE"
        l.save()
        messages.success(request,'Apontamento <b>alterado</b>')
        return redirect('gestao_apontamento_id', id)
    else:
        return render(request,'gestao/apontamento_id.html',{'form':form,'apontamento':apontamento})

@login_required
@permission_required('gestao.dashboard')
def staff_update(request,id):
    staff = Staff.objects.get(pk=id)
    form = StaffForm(request.POST, instance=staff)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "gestao.staff"
        l.objeto_id = registro.id
        l.objeto_str = registro.usuario.username
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Staff <b>{registro.usuario.username}</b> alterado')
        return redirect('gestao_staff_id', id)
    else:
        return render(request,'gestao/staff_id.html',{'form':form,'staff':staff})

@login_required
@permission_required('gestao.dashboard')
def diretriz_update(request,id):
    diretriz = Diretriz.objects.get(pk=id)
    form = DiretrizForm(request.POST, instance=diretriz)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "gestao.diretriz"
        l.objeto_id = registro.id
        l.objeto_str = 'Nao aplicavel'
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Diretriz <b>{registro.id}</b> alterada')
        return redirect('gestao_diretriz_id', id)
    else:
        return render(request,'gestao/diretriz_id.html',{'form':form,'diretriz':diretriz})

@login_required
@permission_required('gestao.dashboard')
def label_update(request,id):
    label = Label.objects.get(pk=id)
    form = LabelForm(request.POST, instance=label)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "gestao.label"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Label <b>{registro.nome}</b> alterada')
        return redirect('gestao_label_id', id)
    else:
        return render(request,'gestao/label_id.html',{'form':form,'label':label})

@login_required
@permission_required('gestao.dashboard')
def analise_update(request,id):
    analise = Analise.objects.get(pk=id)
    form = AnaliseForm(request.POST, instance=analise)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "gestao.analise"
        l.objeto_id = registro.id
        l.objeto_str = 'Nao aplicavel'
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Analise <b>{registro.id}</b> alterada')
        return redirect('gestao_analise_id', id)
    else:
        return render(request,'gestao/analise_id.html',{'form':form,'analise':analise})

@login_required
@permission_required('gestao.dashboard')
def plano_update(request,id):
    plano = Plano.objects.get(pk=id)
    form = PlanoForm(request.POST, instance=plano)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "gestao.plano"
        l.objeto_id = registro.id
        l.objeto_str = registro.titulo[0:40]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Plano <b>alterado</b>')
        return redirect('gestao_plano_id', id)
    else:
        return render(request,'gestao/plano_id.html',{'form':form,'plano':plano})

# METODOS DELETE
@login_required
@permission_required('gestao.dashboard')
def indicador_delete(request,id):
    try:
        registro = Indicador.objects.get(pk=id)
        l = Log()
        l.modelo = "gestao.indicador"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Indicador <b>{registro.nome}</b> apagado. Essa operação não pode ser desfeita')
        return redirect('gestao_indicadores')
    except:
        messages.error(request,'ERRO ao apagar indicador')
        return redirect('gestao_indicador_id', id)

@login_required
@permission_required('gestao.dashboard')
def apontamento_delete(request,id):
    try:
        registro = Apontamento.objects.get(pk=id)
        l = Log()
        l.modelo = "gestao.indicador"
        l.objeto_id = registro.indicador.id
        l.objeto_str = f'{registro.indicador.id}_{registro.referencia}'
        l.usuario = request.user
        l.mensagem = "APONTAMENTO DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Apontamento <b>excluido</b>. Essa operação não pode ser desfeita')
        return redirect('gestao_apontamentos')
    except:
        messages.error(request,'ERRO ao apagar apontamento')
        return redirect('gestao_apontamento_id', id)

@login_required
@permission_required('gestao.dashboard')
def staff_delete(request,id):
    try:
        registro = Staff.objects.get(pk=id)
        l = Log()
        l.modelo = "gestao.staff"
        l.objeto_id = registro.id
        l.objeto_str = registro.usuario.username
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Staff <b>{registro.usuario.username}</b> apagado. Essa operação não pode ser desfeita')
        return redirect('gestao_staffs')
    except:
        messages.error(request,'ERRO ao apagar staff')
        return redirect('gestao_staff_id', id)

@login_required
@permission_required('gestao.dashboard')
def diretriz_delete(request,id):
    try:
        registro = Diretriz.objects.get(pk=id)
        l = Log()
        l.modelo = "gestao.diretriz"
        l.objeto_id = registro.id
        l.objeto_str = 'Nao aplicavel'
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Diretriz <b>apagada</b>. Essa operação não pode ser desfeita')
        return redirect('gestao_dashboard')
    except:
        messages.error(request,'ERRO ao apagar diretriz')
        return redirect('gestao_diretriz_id', id)

@login_required
@permission_required('gestao.dashboard')
def label_delete(request,id):
    try:
        registro = Label.objects.get(pk=id)
        l = Log()
        l.modelo = "gestao.label"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Label <b>{registro.nome}</b> apagada. Essa operação não pode ser desfeita')
        return redirect('gestao_labels')
    except:
        messages.error(request,'ERRO ao apagar label')
        return redirect('gestao_label_id', id)

@login_required
@permission_required('gestao.dashboard')
def analise_delete(request,id):
    try:
        registro = Analise.objects.get(pk=id)
        l = Log()
        l.modelo = "gestao.analise"
        l.objeto_id = registro.id
        l.objeto_str = 'Nao aplicavel'
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Analise <b>apagada</b>. Essa operação não pode ser desfeita')
        return redirect('gestao_analises')
    except:
        messages.error(request,'ERRO ao apagar analise')
        return redirect('gestao_analise_id', id)

@login_required
@permission_required('gestao.dashboard')
def plano_delete(request,id):
    try:
        registro = Plano.objects.get(pk=id)
        l = Log()
        l.modelo = "gestao.plano"
        l.objeto_id = registro.id
        l.objeto_str = registro.titulo[0:40]
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Plano <b>apagado</b>. Essa operação não pode ser desfeita')
        return redirect('gestao_dashboard')
    except:
        messages.error(request,'ERRO ao apagar plano')
        return redirect('gestao_plano_id', id)