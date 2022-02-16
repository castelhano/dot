from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Ocorrencia
from core.models import Empresa
from datetime import date, datetime
from django.db.models import Count

@login_required
@permission_required('trafego.dashboard_ocorrencia')
def ocorrencia_dashboard(request):
    periodo_de = request.GET.get('periodo_de', date.today().replace(day=1))
    periodo_ate = request.GET.get('periodo_ate', date.today())
    ocorrencias = Ocorrencia.objects.filter(data__range=[periodo_de,periodo_ate])
    
    if request.GET.get('empresa', None):
        try:
            if request.user.is_superuser:
                empresa = Empresa.objects.get(id=request.GET.get('empresa', None))
            else:
                empresa = request.user.profile.empresas.filter(id=request.GET.get('empresa', None)).get()
            empresa_nome = empresa.nome
        except:
            messages.error(request,'Empresa <b>não encontrada</b> ou <b>não habilitada</b> para o seu usuário')
            return redirect('trafego_ocorrencia_dashboard')
        ocorrencias = ocorrencias.filter(empresa=empresa)
    else:
        if not request.user.is_superuser:
            ocorrencias = ocorrencias.filter(empresa__in=request.user.profile.empresas.all())
        empresa_nome = None
    
    evolucao_ocorrencias = ocorrencias.values('data').annotate(qtd=Count('data')).order_by()
    ocorrencias_empresa = ocorrencias.values('empresa__nome').annotate(qtd=Count('empresa')).order_by()
    ocorrencias_evento = ocorrencias.values('evento__nome').annotate(qtd=Count('evento')).order_by('-qtd')
    ocorrencias_linha = ocorrencias.values('linha__codigo').annotate(qtd=Count('linha')).exclude(linha=None).order_by('-qtd')
    
    from core.chart_metrics import backgrounds as bg, borders as bc, COLORS as color
    
    evolucao_ocorrencias_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    dias = 0
    for row in evolucao_ocorrencias:
        evolucao_ocorrencias_metrics['categorias'].append(row['data'].day)
        evolucao_ocorrencias_metrics['dados'].append(float(row['qtd']))
        evolucao_ocorrencias_metrics['bgcolors'].append(bg.primary)
        evolucao_ocorrencias_metrics['bordercolors'].append(bc.primary)
        dias += 1
    
    ocorrencias_empresa_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    for step, row in enumerate(ocorrencias_empresa):
        ocorrencias_empresa_metrics['categorias'].append(row['empresa__nome'])
        ocorrencias_empresa_metrics['dados'].append(int(row['qtd']))
        ocorrencias_empresa_metrics['bgcolors'].append(color[step])
        ocorrencias_empresa_metrics['bordercolors'].append(color[step])
    
    ocorrencias_evento_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    for row in ocorrencias_evento:
        ocorrencias_evento_metrics['categorias'].append(row['evento__nome'])
        ocorrencias_evento_metrics['dados'].append(int(row['qtd']))
        ocorrencias_evento_metrics['bgcolors'].append(bg.purple)
        ocorrencias_evento_metrics['bordercolors'].append(bc.purple)
    
    ocorrencias_linha_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    for row in ocorrencias_linha:
        ocorrencias_linha_metrics['categorias'].append(row['linha__codigo'])
        ocorrencias_linha_metrics['dados'].append(int(row['qtd']))
        ocorrencias_linha_metrics['bgcolors'].append(bg.primary)
        ocorrencias_linha_metrics['bordercolors'].append(bc.primary)
    
    
    gravidade = dict(L=0, M=0, G=0)
    indisciplina = 0
    omissao = 0
    for row in ocorrencias:
        gravidade[row.gravidade] += 1
        if row.indisciplina_condutor:
            indisciplina += 1
        if row.viagem_omitida:
            omissao += 1
        
    
    metrics = {
        'periodo_de': periodo_de if isinstance(periodo_de, date) else datetime.strptime(periodo_de, '%Y-%m-%d'),
        'periodo_ate': periodo_ate if isinstance(periodo_ate, date) else datetime.strptime(periodo_ate, '%Y-%m-%d'),
        'qtd_ocorrencias': ocorrencias.count(),
        'gravidade':gravidade,
        'indisciplina':indisciplina,
        'omissao':omissao,
        'empresa_nome':empresa_nome,
        'evolucao_ocorrencias':evolucao_ocorrencias_metrics,
        'ocorrencias_evento':ocorrencias_evento_metrics,
        'ocorrencias_empresa':ocorrencias_empresa_metrics,
        'ocorrencias_linha':ocorrencias_linha_metrics,
    }
    metrics['indisciplina_percentual'] = metrics['indisciplina'] / metrics['qtd_ocorrencias'] * 100 if metrics['qtd_ocorrencias'] > 0 else None
    metrics['omissao_percentual'] = metrics['omissao'] / metrics['qtd_ocorrencias'] * 100 if metrics['qtd_ocorrencias'] > 0 else None
    metrics['media_dia_ocorrencias'] = metrics['qtd_ocorrencias'] / dias if dias > 0 else None
    return render(request, 'trafego/ocorrencia_dashboard.html', {'metrics': metrics})