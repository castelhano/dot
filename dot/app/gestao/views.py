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
        diretrizes = Diretriz.objects.filter(ativo=True, empresa__in=staff.usuario.profile.empresas.all()).order_by('created_on')
    except Exception as e:
        staff = None
        diretrizes = None
    return render(request,'gestao/dashboard.html',{'staff':staff,'diretrizes':diretrizes})

@login_required
@permission_required('gestao.dashboard')
def roadmap(request):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E','G']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    return render(request,'gestao/roadmap.html',{'staff':staff})

@login_required
@permission_required('gestao.dashboard')
def analytics(request):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E','G']:
            raise Exception('Perfil não liberado para este recurso')
        indicadores = Indicador.objects.filter(ativo=True)
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    return render(request,'gestao/analytics.html',{'staff':staff,'indicadores':indicadores})
    
@login_required
@permission_required('gestao.dashboard')
def indicadores(request):
    indicadores = Indicador.objects.all().order_by('nome')
    fields = ['ativo']
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E','G']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    try:
        params = clean_request(request.GET, fields)
        indicadores = indicadores.filter(**params)
        return render(request,'gestao/indicadores.html', {'indicadores' : indicadores,'staff':staff})
    except:
        messages.warning(request,'<b>Erro</b> ao filtrar indicadores')
        return redirect('gestao_indicadores')

@login_required
@permission_required('gestao.dashboard')
def apontamentos(request, indicador):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E','G']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    apontamentos = Apontamento.objects.filter(indicador__id=indicador).order_by('referencia')
    return render(request,'gestao/apontamentos.html', {'apontamentos' : apontamentos,'staff':staff})

@login_required
@permission_required('gestao.dashboard')
def planos_arquivados(request):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E','G']:
            raise Exception('Perfil não liberado para este recurso')
        planos = staff.planos_arquivados()
        if request.method == 'POST':
            pass
        return render(request,'gestao/planos_arquivados.html', {'planos':planos,'staff':staff})    
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
    return redirect('gestao_dashboard')
    

@login_required
@permission_required('gestao.staff')
def staffs(request):
    try:
        staff = Staff.objects.get(usuario=request.user)
    except Exception as e:
        staff = None
    staffs = Staff.objects.all().order_by('usuario__username')
    fields = ['role','usuario__is_active']
    try:
        params = clean_request(request.GET, fields)
        staffs = staffs.filter(**params)
        return render(request,'gestao/staffs.html', {'staffs' : staffs, 'staff':staff})
    except:
        messages.warning(request,'<b>Erro</b> ao filtrar staff')
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
    try:
        staff = Staff.objects.get(usuario=request.user)
        if staff.role != 'M':
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    labels = Label.objects.all().order_by('nome')
    if request.method == 'POST' and request.POST['pesquisa'] != '':
        labels = labels.filter(nome__contains=request.POST['pesquisa'])
    return render(request,'gestao/labels.html', {'labels' : labels,'staff':'staff'})

@login_required
@permission_required('gestao.dashboard')
def analises(request):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E','G']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
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
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
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
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E','G']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
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
@permission_required('gestao.staff')
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
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
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
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
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
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    if request.method == 'POST':
        form = AnaliseForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save(commit=False)
                registro.created_by = request.user
                registro.save()
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
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E','G']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
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
    return render(request,'gestao/plano_add.html',{'form':form,'plano':p,'staff':staff})

# METODOS GET
@login_required
@permission_required('gestao.dashboard')
def indicador_id(request,id):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M', 'E']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    indicador = Indicador.objects.get(pk=id)
    form = IndicadorForm(instance=indicador)
    return render(request,'gestao/indicador_id.html',{'form':form,'indicador':indicador,'staff':staff})

@login_required
@permission_required('gestao.dashboard')
def apontamento_id(request,id):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E','G']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    apontamento = Apontamento.objects.get(pk=id)
    form = ApontamentoForm(instance=apontamento)
    return render(request,'gestao/apontamento_id.html',{'form':form,'apontamento':apontamento})

@login_required
@permission_required('gestao.staff')
def staff_id(request,id):
    staff = Staff.objects.get(pk=id)
    form = StaffForm(instance=staff)
    return render(request,'gestao/staff_id.html',{'form':form,'staff':staff})

@login_required
@permission_required('gestao.dashboard')
def diretriz_id(request,id):
    try:
        staff = Staff.objects.get(usuario=request.user)
    except Exception as e:
        messages.error(request, f'É necessário fazer parte da <b>Staff</b>')
        return redirect('gestao_dashboard')
    diretriz = Diretriz.objects.get(pk=id)
    form = DiretrizForm(instance=diretriz)
    return render(request,'gestao/diretriz_id.html',{'form':form,'diretriz':diretriz,'staff':staff})

@login_required
@permission_required('gestao.dashboard')
def label_id(request,id):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    label = Label.objects.get(pk=id)
    form = LabelForm(instance=label)
    return render(request,'gestao/label_id.html',{'form':form,'label':label})

@login_required
@permission_required('gestao.dashboard')
def analise_id(request,id):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    analise = Analise.objects.get(pk=id)
    form = AnaliseForm(instance=analise)
    return render(request,'gestao/analise_id.html',{'form':form,'analise':analise})

@login_required
@permission_required('gestao.dashboard')
def plano_id(request,id):
    try:
        staff = Staff.objects.get(usuario=request.user)
    except Exception as e:
        messages.error(request,f'É necessário fazer parte da <b>Staff</b> {e}')
        return redirect('gestao_dashboard')
    plano = Plano.objects.get(pk=id)
    if not staff.usuario.profile.allow_empresa(plano.diretriz.empresa.id): # Verifica se usuario tem acesso a empresa definida na diretriz
        messages.error(request,'Empresa não habilitada para seu usuário')
        return redirect('gestao_dashboard')
    form = PlanoForm(instance=plano)
    return render(request,'gestao/plano_id.html',{'form':form,'plano':plano,'staff':staff})

# METODOS UPDATE
@login_required
@permission_required('gestao.dashboard')
def indicador_update(request,id):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
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
    try:
        staff = Staff.objects.get(usuario=request.user)
        apontamento = Apontamento.objects.get(pk=id)
        if not staff.role in ['M','E','G']:
            raise Exception('Perfil não liberado para este recurso')
        if not staff.usuario.profile.allow_empresa(apontamento.empresa.id): # Verifica se usuario tem acesso a empresa
            raise Exception('Empresa não habilitada para seu usuário')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
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
@permission_required('gestao.staff')
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
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E']:
            raise Exception('Perfil não liberado para atualizar diretriz')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
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
def diretriz_finalizar(request):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M']:
            raise Exception('Perfil não liberado para este recurso')
        diretriz = Diretriz.objects.get(id=request.POST['diretriz'])
        diretriz.ativo = False
        diretriz.save()
        l = Log()
        l.modelo = "gestao.diretriz"
        l.objeto_id = diretriz.id
        l.objeto_str = diretriz.titulo[0:40]
        l.usuario = request.user
        l.mensagem = "FINALIZADA"
        l.save()
        for plano in diretriz.planos():
            plano.status = 'C'
            plano.save()
        messages.success(request,f'Diretriz <b>finalizada</b>')    
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
    return redirect('gestao_dashboard')

@login_required
@permission_required('gestao.dashboard')
def diretriz_reativar(request, id):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M']:
            raise Exception('Perfil não liberado para este recurso')
        diretriz = Diretriz.objects.get(pk=id)
        diretriz.ativo = True
        diretriz.save()
        l = Log()
        l.modelo = "gestao.diretriz"
        l.objeto_id = diretriz.id
        l.objeto_str = diretriz.titulo[0:40]
        l.usuario = request.user
        l.mensagem = "REATIVADA"
        l.save()
        for plano in diretriz.planos():
            plano.status = 'A'
            plano.save()
        messages.success(request,f'Diretriz <b>reativada</b>')    
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
    return redirect('gestao_dashboard')

@login_required
@permission_required('gestao.dashboard')
def label_update(request,id):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
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
    try:
        staff = Staff.objects.get(usuario=request.user)
        analise = Analise.objects.get(pk=id)
        if analise.created_by != request.user and not staff.role in ['M']:
            raise Exception(f'Só pode ser editada pelo <b>responsável</b>: {analise.created_by.username.title()}')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
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
    try:
        staff = Staff.objects.get(usuario=request.user)
        plano = Plano.objects.get(pk=id)
        if not staff.role in ['M','E'] and plano.responsavel != staff:
            raise Exception(f'Somente o <b>responsável ou gestor</b> pode editar este plano')
        if not staff.usuario.profile.allow_empresa(plano.diretriz.empresa.id): # Verifica se usuario tem acesso a empresa
            raise Exception('Empresa não habilitada para seu usuário')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
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

@login_required
@permission_required('gestao.dashboard')
def plano_movimentar(request,id):
    operacao = request.GET.get('operacao', None)
    try:
        staff = Staff.objects.get(usuario=request.user)
        plano = Plano.objects.get(id=id)
        if operacao == 'execucao' and not staff.role in ['M','E']:
            raise Exception('Perfil não liberado para este recurso')
        if operacao == 'revisao' and not staff.role in ['M','E'] and request.user != plano.responsavel.usuario:
            raise Exception('Somente o responsável pode enviar para revisão')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    try:
        l = Log()
        l.modelo = "gestao.plano"
        l.objeto_id = plano.id
        l.objeto_str = plano.titulo[0:40]
        l.usuario = request.user
        if operacao == 'revisao':
            plano.status = 'A'
            l.mensagem = "ENVIADO REVISAO"
        elif operacao == 'execucao':
            plano.status = 'E'
            l.mensagem = "RETORNADO"
        else:
            messages.error(request,f'Operação <b>inválida</b>')
            return redirect('gestao_dashboard')
        plano.save()
        l.save()
    except Exception as e:
        messages.error(request,f'<b>Erro</b>: {e}')
    return redirect('gestao_dashboard')

@login_required
@permission_required('gestao.dashboard')
def plano_avaliar(request):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if staff.role in ['M', 'E']:
            plano = Plano.objects.get(id=request.POST['plano'])
            plano.conclusao = int(request.POST['conclusao'])
            plano.avaliacao = int(request.POST['avaliacao'])
            plano.save()
            l = Log()
            l.modelo = "gestao.plano"
            l.objeto_id = plano.id
            l.objeto_str = plano.titulo[0:40]
            l.usuario = request.user
            l.mensagem = "AVALIACAO ADD"
            l.save()        
        else:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro:</b> {e}')
    return redirect('gestao_dashboard') 

# METODOS DELETE
@login_required
@permission_required('gestao.dashboard')
def indicador_delete(request,id):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
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
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E','G']:
            raise Exception('Perfil não liberado para este recurso')
        if not staff.usuario.profile.allow_empresa(regitro.empresa.id): # Verifica se usuario tem acesso a empresa
            raise Exception('Empresa não habilitada para seu usuário')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    try:
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
@permission_required('gestao.staff')
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
        staff = Staff.objects.get(usuario=request.user)
        registro = Diretriz.objects.get(pk=id)
        if not staff.role in ['M','E']:
            raise Exception('Perfil não liberado para este recurso')
        if not staff.usuario.profile.allow_empresa(registro.empresa.id): # Verifica se usuario tem acesso a empresa
            raise Exception('Empresa não habilitada para seu usuário')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    try:
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
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
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
        staff = Staff.objects.get(usuario=request.user)
        analise = Analise.objects.get(pk=id)
        if analise.created_by != request.user and not staff.role in ['M']:
            raise Exception(f'Só pode ser excluida pelo <b>responsável</b>: {analise.created_by.username.title()}')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
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
        staff = Staff.objects.get(usuario=request.user)
        registro = Plano.objects.get(pk=id)
        if not staff.role in ['M']:
            raise Exception('Perfil não liberado para este recurso')
        if not staff.usuario.profile.allow_empresa(registro.diretriz.empresa.id): # Verifica se usuario tem acesso a empresa
            raise Exception('Empresa não habilitada para seu usuário')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    try:
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