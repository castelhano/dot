# from django.http import HttpResponse
# from json import dumps
import re
from django.urls import reverse
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from .models import Indicador, Apontamento, Staff, Diretriz, Label, Analise, Plano, Settings
from .forms import IndicadorForm, ApontamentoForm, StaffForm, DiretrizForm, LabelForm, PlanoForm, SettingsForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.contrib.auth.models import User
from core.models import Log, Empresa, Alerta
from core.extras import clean_request
from datetime import date, datetime, timedelta

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
        empresa = request.GET.get('empresa', None)
        empresas = request.user.profile.empresas.all()
        if empresa:
            empresa = Empresa.objects.get(id=empresa)
        elif empresas.count() > 0:
            empresa = empresas.first()
        else:
            messages.warning(request,'É necessário ter pelo menos uma <b>empresa</b> habilitada para seu usuario')
            return redirect('gestao_dashboard')
        indicadores = Indicador.objects.filter(ativo=True).order_by('nome')
        if not Plano.objects.filter(diretriz__empresa=empresa, diretriz__ativo=True).exclude(inicio=None).exclude(termino=None).exists():
            messages.warning(request,'<b>Atenção</b> Não existe nenhum plano (com prazo) ativo para exibir no roadmap')
            return redirect('gestao_dashboard')        
        inicio = Plano.objects.filter(diretriz__empresa=empresa, diretriz__ativo=True).order_by('inicio').first().inicio
        termino = Plano.objects.filter(diretriz__empresa=empresa, diretriz__ativo=True).order_by('termino').last().termino
        view_range = ((termino.month - inicio.month) + (termino.year - inicio.year) * 12) + 1
        meses = []
        for _ in range(0, view_range):
            meses.append([f'{termino.strftime("%b").title()} {termino.strftime("%y").title()}',termino.strftime("%m")])
            termino = termino.replace(day=1) - timedelta(days=1)
        meses.reverse()

        metrics = {
            'staff':staff,
            'empresa':empresa,
            'empresas':empresas,
            'indicadores':indicadores,
            'meses':meses,
            'dias_plot':view_range * 30,
            'inicio_plot':inicio.replace(day=1),
        }
    except Empresa.DoesNotExist:
        messages.error(request,f'<b>Erro</b> Empresa não encontrada ou não habilitada')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    return render(request,'gestao/roadmap.html',metrics)

@login_required
@permission_required('gestao.dashboard')
def analytics(request):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E','G']:
            raise Exception('Perfil não liberado para este recurso')
        empresa = request.GET.get('empresa', None)
        empresas = request.user.profile.empresas.all()
        if empresa:
            empresa = Empresa.objects.get(id=empresa)
        elif empresas.count() > 0:
            empresa = empresas.first()
        else:
            messages.warning(request,'É necessário ter pelo menos uma <b>empresa</b> habilitada para seu usuario')
            return redirect('gestao_dashboard')
        try: # Carrega configuracoes do app
            settings = Settings.objects.all().get()
        except: # Caso nao gerado configuracoes iniciais carrega definicoes basicas
            settings = Settings()
        
        # Exibe ultimo conforme definido nas configuracoes (mes atual ou anterior)
        if settings.analytics_foco_mes_atual:
            target = datetime.now()
        else:
            target = (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1)
        metrics = {
            'empresa':empresa,
            'empresas':empresas,
            'indicadores':Indicador.objects.filter(ativo=True).order_by('nome'),
            'periodo':int(request.GET.get('periodo', 3)),
            'meses':[target.strftime("%B").title()],
            'referencias':[f'{target.year}_{str(target.month).zfill(2)}'],
            'apontamento_form':ApontamentoForm(),
        }
        for _ in range(1, metrics['periodo']):
            target = target.replace(day=1) - timedelta(days=1)
            metrics['meses'].append(target.strftime("%B").title())
            metrics['referencias'].append(f'{target.year}_{str(target.month).zfill(2)}')
        metrics['meses'].reverse()
        metrics['referencias'].reverse()
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    return render(request,'gestao/analytics.html',{'staff':staff,'metrics':metrics})

@login_required
@permission_required('gestao.dashboard')
def stratified(request):
    try:
        indicador = Indicador.objects.get(id=request.GET['indicador'])
        empresas = request.user.profile.empresas.all()
        empresa = empresas.get(id=request.GET['empresa'])
    except:
        messages.error(request,f'<b>Erro</b> Indicador ou empresa inválido')
        return redirect('gestao_analytics')
    de = request.GET.get('de', None)
    ate = request.GET.get('ate', None)
    if not de or not ate:
        intervalo = 12
        today_m = date.today().month - 1 if date.today().month > 1 else 12
        today_y = date.today().year if date.today().month > 1 else date.today().year - 1
        de_m = today_m - (intervalo - 1)
        de_y = today_y
        while de_m < 0:
            de_m += 12
            de_y -= 1        
        de = f'{de_y}_{str(de_m).zfill(2)}'
        ate = f'{today_y}_{str(today_m).zfill(2)}'
    else:
        de = de.replace('-','_')
        ate = ate.replace('-','_')
    apontamentos = Apontamento.objects.filter(referencia__range=(de,ate), indicador=indicador, empresa=empresa).order_by('referencia')
    
    from core.chart_metrics import backgrounds as bg, borders as bc, COLORS as color
    evolucao_indicador = {
        'categorias':[],
        'dados':[],
        'metas':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    min = None
    for row in apontamentos:
        evolucao_indicador['categorias'].append(row.referencia)
        evolucao_indicador['dados'].append(float(row.valor))
        evolucao_indicador['metas'].append(float(row.meta) if row.meta > 0 else None)
        evolucao_indicador['bgcolors'].append(bg.purple)
        evolucao_indicador['bordercolors'].append(bc.purple)
        if not min or row.valor < min or (row.meta < min and row.meta > 0):
            min = row.valor if row.valor < row.meta else row.meta
    
    metrics = {
    'indicador':indicador,
    'empresa':empresa,
    'de':de.replace('_','-'),
    'ate':ate.replace('_','-'),
    'empresas':empresas,
    'apontamentos':apontamentos,
    'indicadores':Indicador.objects.all().exclude(id=indicador.id),
    'evolucao_indicador':evolucao_indicador,
    'chart_min': str(round(float(min) * 0.98,1)) if min else '',
    }
    return render(request, 'gestao/stratified.html', metrics)
    
@login_required
def settings(request):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard') 
    try: # Busca configuracao do app
        settings = Settings.objects.all().get()
    except: # Caso ainda nao configurado, inicia com configuracao basica
        if Settings.objects.all().count() == 0:
            settings = Settings()
            settings.save()
            l = Log()
            l.modelo = "gestao.settings"
            l.objeto_id = settings.id
            l.objeto_str = 'n/a'
            l.usuario = request.user
            l.mensagem = "AUTO CREATED"
            l.save()
            messages.warning(request,'<b>Informativo:</b> App configurado pela primeira vez')
        else:
            settings = None
            messages.error(request,'<b>Erro::</b> Identificado duplicatas nas configurações do sistema, entre em contato com o administrador.')
    form = SettingsForm(instance=settings)
    return render(request,'gestao/settings.html',{'form':form,'settings':settings})

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
def planos_arquivo(request):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E','G']:
            raise Exception('Perfil não liberado para este recurso')
        planos = staff.planos_arquivados()
        if request.method == 'POST':
            pass
        return render(request,'gestao/planos_arquivo.html', {'planos':planos,'staff':staff})
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
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E','G']:
            raise Exception('Perfil não liberado para este recurso')        
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    diretrizes = Diretriz.objects.filter(ativo=False).order_by('created_on','indicador__nome')
    return render(request,'gestao/diretrizes.html', {'diretrizes' : diretrizes, 'staff':staff})

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
    try:
        analises = Analise.objects.all().order_by('created_on')
        if request.GET.get('indicador', None):
            analises = analises.filter(indicador__id=request.GET['indicador'])        
        if request.GET.get('archive', None) != 'True':
            analises = analises.filter(concluido=False)
        if request.GET.get('empresa', None):
            empresa = request.user.profile.empresas.get(id=request.GET['empresa'])
            analises = analises.filter(empresa=empresa)
        else:
            empresa = None
        metrics = {
            'staff':staff,
            'lembretes' : analises.filter(tipo='L', created_by=request.user),
            'melhorias' : analises.filter(tipo='M'),
            'nao_conforme' : analises.filter(tipo='N'),
            'empresa' : empresa
        }
    except Empresa.DoesNotExist as e:
        messages.error(request,'Empresa não <b>encontrada ou não habilitada</b>')
        return redirect('gestao_analises')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    return render(request,'gestao/analises.html', metrics)

@login_required
@permission_required('gestao.dashboard')
def analise_arquivo(request):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M','E','G']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    try:
        metrics = {
        'staff':staff,
        'empresas':staff.usuario.profile.empresas.all(),
        'empresa':None if not request.GET.get('empresa', None) else Empresa.objects.get(id=request.GET['empresa']),
        'tipo_display':None if not request.GET.get('tipo', None) else dict(Analise.TIPO_CHOICES)[request.GET['tipo']]
        }
        if metrics['empresa'] and metrics['tipo_display']:            
            analises = Analise.objects.filter(empresa=metrics['empresa'],tipo=request.GET['tipo'])            
            if staff.role != 'M':
                analises = analises.filter(created_by=request.user)
            metrics['analises'] = analises        
        return render(request,'gestao/analise_arquivo.html',metrics)
    except Empresa.DoesNotExist as e:
        messages.error(request,'<b>Erro</b> empresa não encontrada ou não habilitada')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
    return render(request,'gestao/analise_arquivo.html')

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

def gte(v1, v2, qmm=True):
    if qmm:
        if v1 > v2:
            return 1
        elif v2 > v1:
            return -1
        else:
            return 0
    else:
        if v1 > v2:
            return -1
        elif v2 > v1:
            return 1
        else:
            return 0

@login_required
@permission_required('gestao.add_apontamento')
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
                ano = request.POST['ano']
                mes = request.POST['mes'].zfill(2)
                # Verifica se ano e mes tem formato valido
                if re.search('^(19|20)\d{2}$', ano) and mes in ['01','02','03','04','05','06','07','08','09','10','11','12']:
                    registro.referencia = f"{ano}_{mes}"
                    registro.meta = registro.indicador.meta
                    # Levanta se indicador tem registro no mes anterior para comparar evolucao
                    if int(mes) > 0:
                        ultima_referencia = f"{ano}_{str(int(mes) - 1).zfill(2)}"
                    else:
                        ultima_referencia = f"{int(ano) - 1}_12"
                    if Apontamento.objects.filter(empresa=registro.empresa,indicador=registro.indicador,referencia=ultima_referencia).exists():
                        mes_anterior = Apontamento.objects.get(empresa=registro.empresa,indicador=registro.indicador,referencia=ultima_referencia)
                        registro.evolucao = gte(float(registro.valor),float(mes_anterior.valor),registro.indicador.quanto_maior_melhor)
                    else:
                        registro.evolucao = 0
                    # Verifica se apontamento ja existe, se sim faz update no registro atual
                    if not Apontamento.objects.filter(empresa=registro.empresa,indicador=registro.indicador,referencia=registro.referencia).exists():
                        registro.save()
                        messages.success(request,'Apontamento <b>inserido</b>')
                    else: # Caso exista, atualiza apontamento
                        apontamento = Apontamento.objects.filter(empresa=registro.empresa,indicador=registro.indicador,referencia=registro.referencia).get()
                        apontamento.valor = registro.valor
                        apontamento.evolucao = registro.evolucao
                        apontamento.save()
                        registro = apontamento
                        messages.success(request,'Apontamento <b>atualizado</b>')
                    # Verifica se existe apontamentos posteriores ao lancado, se sim atualiza no mes subsequente
                    if int(mes) < 12:
                        proxima_referencia = f"{ano}_{str(int(mes) + 1).zfill(2)}"
                    else:
                        proxima_referencia = f"{int(ano) + 1}_01"
                    if Apontamento.objects.filter(empresa=registro.empresa,indicador=registro.indicador,referencia=proxima_referencia).exists():
                        apontamento_posterior = Apontamento.objects.filter(empresa=registro.empresa,indicador=registro.indicador,referencia=proxima_referencia).get()
                        apontamento_posterior.evolucao = gte(float(apontamento_posterior.valor),float(registro.valor),registro.indicador.quanto_maior_melhor)
                        apontamento_posterior.save()
                    l = Log()
                    l.modelo = "gestao.indicador"
                    l.objeto_id = registro.indicador.id
                    l.objeto_str = f'{registro.indicador.id}_{registro.referencia}'
                    l.usuario = request.user
                    l.mensagem = "APONTAMENTO ADD"
                    l.save()
                else:
                    raise Exception('Período informado <b>inválido</b>')
                base_url = reverse('gestao_analytics')
                query_string =  urlencode({'empresa': registro.empresa.id})
                url = '{}?{}'.format(base_url, query_string)
                return redirect(url)
            except Exception as e:
                messages.error(request,f'Erro: {e}')
                return redirect('gestao_analytics')
        return render(request, 'core/index.html',{'form':form})
    else:
        messages.error(request,'Operação inválida')
        return redirect('index')

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
                # Cria alerta para pessoal na staff sobre nova diretriz
                staffs = Staff.objects.filter(usuario__is_active=True, usuario__profile__empresas=registro.empresa).exclude(usuario=request.user)
                params = {
                    'titulo':'Nova Diretriz criada',
                    'mensagem':f'<b>{registro.titulo}</b><br />Empresa: <b>{registro.empresa.nome}</b> <br />Indicador: <b>{registro.indicador.nome}</b>',
                    'link': f'gestao_diretriz_id/{registro.id}'
                }
                for item in staffs:
                    params['usuario'] = item.usuario                    
                    Alerta.objects.create(**params)
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
        try:
            analise = Analise()
            analise.empresa = Empresa.objects.get(id=request.POST['empresa'])
            analise.indicador = Indicador.objects.get(id=request.POST['indicador'])
            if 'critico' in request.POST:
                analise.critico = True
            analise.tipo = request.POST['tipo']
            analise.descricao = request.POST['descricao']
            analise.created_by = request.user
            analise.save()
            l = Log()
            l.modelo = "gestao.analise"
            l.objeto_id = analise.id
            l.objeto_str = f'{analise.id}_{analise.created_by.username.upper()}_{analise.created_on}'
            l.usuario = request.user
            l.mensagem = "CREATED"
            l.save()
            # Se analise for nao conforme ou melhoria gera alerta para staffs no grupo Manager informando da nova analise
            if analise.tipo in ['N','M']:
                staffs = Staff.objects.filter(role__in=['M','E','G'], usuario__is_active=True).exclude(usuario=analise.created_by)
                params = {
                    'titulo':'Nova análise crítica inserida',
                    'mensagem':f'ID: <b>{analise.id}</b> <br />Tipo: <b>{analise.get_tipo_display()}</b> <br />Critico: <b>{analise.critico}</b> <br />Responsável: <b>{analise.created_by.username.title()}</b>',
                    'link': 'gestao_analises'
                }
                for item in staffs:
                    params['usuario'] = item.usuario                    
                    Alerta.objects.create(**params)
            messages.success(request,f'Analise ID: <b>{analise.id}</b> inserida')
            base_url = reverse('gestao_analytics')
            query_string =  urlencode({'empresa': analise.empresa.id})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
        except Exception as e:
            messages.error(request,f'Erro: {e}')
            return redirect('gestao_analytics')
    else:
        messages.error(request,'Requisição inválida')
    return redirect('gestao_dashboard')

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
        return render(request,'gestao/diretriz_id.html',{'form':form,'diretriz':diretriz,'staff':staff})

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
def analise_update(request):
    try:
        staff = Staff.objects.get(usuario=request.user)
        analise = Analise.objects.get(pk=request.POST['id'])
        if analise.created_by != request.user and not staff.role in ['M']:
            raise Exception(f'Só pode ser editada pelo <b>responsável</b>: {analise.created_by.username.title()}')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard')
    try:
        analise.descricao = request.POST['descricao']
        analise.tipo = request.POST['tipo']
        if 'critico' in request.POST:
            analise.critico = True
        else:
            analise.critico = False
        analise.save()
        l = Log()
        l.modelo = "gestao.analise"
        l.objeto_id = analise.id
        l.objeto_str = f'{analise.id}_{analise.created_by.username.upper()}_{analise.created_on}'
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Analise <b>{analise.id}</b> alterada')
    except Exception as e:
        messages.error(request,f'<b>Erro:</b> {e}')
    return redirect('gestao_analises')

@login_required
@permission_required('gestao.dashboard')
def analise_movimentar(request):
    try:
        operacao = request.POST['operacao']
        staff = Staff.objects.get(usuario=request.user)
        analise = Analise.objects.get(id=request.POST['id'])
        if not staff.role in ['M'] and analise.created_by != request.user:
            raise Exception(f'Somente o responsável pode editar: <b>{analise.created_by.username.title()}</b>')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_analises')
    try:
        l = Log()
        l.modelo = "gestao.analise"
        l.objeto_id = analise.id
        l.objeto_str = f'{analise.id}_{analise.created_by.username.upper()}_{analise.created_on}'
        l.usuario = request.user
        if operacao == 'concluir':
            analise.concluido = True
            l.mensagem = "CONCLUIDO"
            messages.success(request,f'Análise <b>concluída</b>')
        else:
            messages.error(request,f'Operação <b>inválida</b>')
            return redirect('gestao_analises')
        analise.save()
        l.save()
    except Exception as e:
        messages.error(request,f'<b>Erro</b>: {e}')
    return redirect('gestao_analises')

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
        if plano.bloqueado and not staff.role == 'M':
            raise Exception('Plano bloqueado para edição')
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
        if operacao in ['execucao','lock','unlock'] and not staff.role in ['M','E']:
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
        elif operacao == 'lock':
            plano.bloqueado = True
            l.mensagem = "BLOQUEADO"
        elif operacao == 'unlock':
            plano.bloqueado = False
            l.mensagem = "DESBLOQUEADO"
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

@login_required
def settings_update(request, id):
    try:
        staff = Staff.objects.get(usuario=request.user)
        if not staff.role in ['M']:
            raise Exception('Perfil não liberado para este recurso')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_dashboard') 
    settings = Settings.objects.get(pk=id)
    form = SettingsForm(request.POST, instance=settings)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "gestao.settings"
        l.objeto_id = registro.id
        l.objeto_str = 'n/a'
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Settings <b>gestao</b> alterado')
        return redirect('gestao_settings')
    else:
        return render(request,'gestao/settings.html',{'form':form,'settings':settings})
        
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
@permission_required('gestao.add_apontamento')
def apontamento_delete(request):
    try:
        ano = request.POST['ano']
        mes = request.POST['mes'].zfill(2)
        # Verifica se ano e mes tem formato valido
        if not re.search('^(19|20)\d{2}$', ano) or mes not in ['01','02','03','04','05','06','07','08','09','10','11','12']:
            raise Exception('Periodo inválido, verifique os dados digitados')
        referencia = f"{ano}_{mes}"
        l = Log()
        l.modelo = "gestao.indicador"
        registro = Apontamento.objects.filter(empresa__id=request.POST['empresa'],indicador__id=request.POST['indicador'], referencia=referencia).get()
        l.objeto_id = registro.indicador.id
        l.objeto_str = f'{registro.indicador.id}_{registro.referencia}'
        l.usuario = request.user
        l.mensagem = "APONTAMENTO DELETE"
        registro.delete()
        l.save()
        # Verifica se existe apontamento posterior, se sim atualiza a evolucao
        if int(mes) < 12:
            proxima_referencia = f"{ano}_{str(int(mes) + 1).zfill(2)}"
        else:
            proxima_referencia = f"{int(ano) + 1}_01"
        if Apontamento.objects.filter(empresa=registro.empresa,indicador=registro.indicador,referencia=proxima_referencia).exists():
            mes_posterior = Apontamento.objects.get(empresa=registro.empresa,indicador=registro.indicador,referencia=proxima_referencia)
            mes_posterior.evolucao = 0
            mes_posterior.save()
        messages.warning(request,f'Apontamento <b>excluido</b>')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
    return redirect('gestao_analytics')

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
        l.objeto_str = registro.titulo[0:40]
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
def analise_delete(request):
    try:
        staff = Staff.objects.get(usuario=request.user)
        analise = Analise.objects.get(pk=request.POST['id'])
        if analise.created_by != request.user and not staff.role == 'M':
            raise Exception(f'Só pode ser excluida pelo responsável: <b>{analise.created_by.username.title()}</b>')
    except Exception as e:
        messages.error(request,f'<b>Erro</b> {e}')
        return redirect('gestao_analises')
    try:
        l = Log()
        l.modelo = "gestao.analise"
        l.objeto_id = analise.id
        l.objeto_str = f'{analise.id}_{analise.created_by.username.upper()}_{analise.created_on}'
        l.usuario = request.user
        l.mensagem = "DELETE"
        analise.delete()
        l.save()
        messages.warning(request,f'Analise <b>apagada</b>. Essa operação não pode ser desfeita')
        return redirect('gestao_analises')
    except:
        messages.error(request,'ERRO ao apagar analise')
        return redirect('gestao_analises')

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