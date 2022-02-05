from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Ocorrencia
from datetime import date
# from datetime import date, datetime, timedelta
# from django.db.models.functions import TruncMonth
from django.db.models import Count

@login_required
@permission_required('trafego.view_ocorrencia')
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
        except:
            messages.error(request,'Empresa <b>não encontrada</b> ou <b>não habilitada</b> para o seu usuário')
            return redirect('trafego_ocorrencia_dashboard')
        ocorrencias = ocorrencias.filter(empresa=empresa)
    else:
        if not request.user.is_superuser:
            ocorrencias = ocorrencias.filter(empresa__in=request.user.profile.empresas.all())
    
    evolucao_ocorrencias = ocorrencias.values('data').annotate(qtd=Count('data')).order_by()
    ocorrencias_empresa = ocorrencias.values('empresa__nome').annotate(qtd=Count('empresa')).order_by()
    ocorrencias_evento = ocorrencias.values('evento__nome').annotate(qtd=Count('evento')).order_by()
    ocorrencias_linha = ocorrencias.values('linha__codigo').annotate(qtd=Count('linha')).order_by()
    
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
        'periodo_de': periodo_de,
        'periodo_ate': periodo_ate,
        'qtd_ocorrencias': ocorrencias.count(),
        'gravidade':gravidade,
        'indisciplina':indisciplina,
        'omissao':omissao,
        'evolucao_ocorrencias':evolucao_ocorrencias_metrics,
    }
    metrics['indisciplina_percentual'] = metrics['indisciplina'] / metrics['qtd_ocorrencias'] * 100 if metrics['qtd_ocorrencias'] > 0 else None
    metrics['omissao_percentual'] = metrics['omissao'] / metrics['qtd_ocorrencias'] * 100 if metrics['qtd_ocorrencias'] > 0 else None
    metrics['media_dia_ocorrencias'] = metrics['qtd_ocorrencias'] / dias if dias > 0 else None
    return render(request, 'trafego/ocorrencia_dashboard.html', {'metrics': metrics})