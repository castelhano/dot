from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Reclamacao
from core.models import Empresa
from datetime import date, datetime
# from django.db.models.functions import TruncMonth
from django.db.models import Count


@login_required
@permission_required('sac.dashboard_reclamacao', login_url="/handler/403")
def reclamacao_dashboard(request):
    periodo_de = request.GET.get('periodo_de', date.today().replace(day=1))
    periodo_ate = request.GET.get('periodo_ate', date.today())
    reclamacoes = Reclamacao.objects.filter(data__range=[periodo_de,periodo_ate])
    
    if request.GET.get('empresa', None):
        try:
            empresa = request.user.profile.empresas.filter(id=request.GET.get('empresa', None)).get()
            reclamacoes = reclamacoes.filter(empresa=empresa)
        except:
            messages.error(request,'Empresa <b>não encontrada</b> ou <b>não habilitada</b> para o seu usuário')
            return redirect('sac_reclamacao_dashboard')
    else:
        reclamacoes = reclamacoes.filter(empresa__in=request.user.profile.empresas.all())
        empresa = None
    evolucao_reclamacoes = reclamacoes.values('data').annotate(qtd=Count('data')).order_by()
    reclamacoes_empresa = reclamacoes.values('empresa__nome').annotate(qtd=Count('empresa')).order_by()
    reclamacoes_classificacao = reclamacoes.values('classificacao__nome').annotate(qtd=Count('classificacao')).exclude(classificacao=None).order_by('-qtd')
    reclamacoes_linha = reclamacoes.values('linha__codigo').annotate(qtd=Count('linha')).exclude(linha=None).order_by('-qtd')
    
    from core.chart_metrics import backgrounds as bg, borders as bc, COLORS as color
    
    evolucao_reclamacoes_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    for row in evolucao_reclamacoes:
        evolucao_reclamacoes_metrics['categorias'].append(f'{str(row["data"].day).zfill(2)}/{str(row["data"].month).zfill(2)}')
        evolucao_reclamacoes_metrics['dados'].append(float(row['qtd']))
        evolucao_reclamacoes_metrics['bgcolors'].append(bg.purple)
        evolucao_reclamacoes_metrics['bordercolors'].append(bc.purple)
    
    reclamacoes_empresa_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    for step, row in enumerate(reclamacoes_empresa):
        reclamacoes_empresa_metrics['categorias'].append(row['empresa__nome'])
        reclamacoes_empresa_metrics['dados'].append(int(row['qtd']))
        reclamacoes_empresa_metrics['bgcolors'].append(color[step])
        reclamacoes_empresa_metrics['bordercolors'].append(color[step])
    
    reclamacoes_classificacao_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    for row in reclamacoes_classificacao:
        reclamacoes_classificacao_metrics['categorias'].append(row['classificacao__nome'])
        reclamacoes_classificacao_metrics['dados'].append(int(row['qtd']))
        reclamacoes_classificacao_metrics['bgcolors'].append(bg.purple)
        reclamacoes_classificacao_metrics['bordercolors'].append(bc.purple)
    
    reclamacoes_linha_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    for row in reclamacoes_linha:
        reclamacoes_linha_metrics['categorias'].append(row['linha__codigo'])
        reclamacoes_linha_metrics['dados'].append(int(row['qtd']))
        reclamacoes_linha_metrics['bgcolors'].append(bg.purple)
        reclamacoes_linha_metrics['bordercolors'].append(bc.purple)
    
    
    metrics = {
        'periodo_de': periodo_de if isinstance(periodo_de, date) else datetime.strptime(periodo_de, '%Y-%m-%d'),
        'periodo_ate': periodo_ate if isinstance(periodo_ate, date) else datetime.strptime(periodo_ate, '%Y-%m-%d'),
        'qtd_reclamacoes': reclamacoes.count(),
        'reclamacoes_site': reclamacoes.filter(origem='S').count(),
        'reclamacoes_abertas': reclamacoes.filter(tratado=False).count(),
        'empresa':empresa,
        'evolucao_reclamacoes':evolucao_reclamacoes_metrics,
        'reclamacoes_classificacao':reclamacoes_classificacao_metrics,
        'reclamacoes_empresa':reclamacoes_empresa_metrics,
        'reclamacoes_linha':reclamacoes_linha_metrics,
    }
    return render(request, 'sac/reclamacao_dashboard.html', metrics)