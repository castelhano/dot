from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
# from .models import Acidente, Terceiro, Despesa, Termo, Paragrafo
# from core.models import Empresa, Log
# from datetime import date, datetime
# from django.db.models.functions import TruncMonth
# from django.db.models import Count, Sum


@login_required
@permission_required('sac.dashboard_reclamacao')
def reclamacao_dashboard(request):
    periodo_de = request.GET.get('periodo_de', date.today().replace(day=1))
    periodo_ate = request.GET.get('periodo_ate', date.today())
    reclamacoes = Acidente.objects.filter(data__range=[periodo_de,periodo_ate])
    
    if request.GET.get('empresa', None):
        try:
            if request.user.is_superuser:
                empresa = Empresa.objects.get(id=request.GET.get('empresa', None))
            else:
                empresa = request.user.profile.empresas.filter(id=request.GET.get('empresa', None)).get()
            empresa_nome = empresa.nome
        except:
            messages.error(request,'Empresa <b>não encontrada</b> ou <b>não habilitada</b> para o seu usuário')
            return redirect('sac_reclamacao_dashboard')
        reclamacoes = reclamacoes.filter(empresa=empresa)
    else:
        if not request.user.is_superuser:
            reclamacoes = reclamacoes.filter(empresa__in=request.user.profile.empresas.all())
        empresa_nome = None
    evolucao_reclamacoes = reclamacoes.values('data').annotate(qtd=Count('data')).order_by()
    reclamacoes_empresa = reclamacoes.values('empresa__nome').annotate(qtd=Count('empresa')).order_by()
    reclamacoes_classificacao = reclamacoes.values('classificacao__nome').annotate(qtd=Count('classificacao')).exclude(classificacao=None).order_by('-qtd')
    reclamacoes_linha = reclamacoes.values('linha__codigo').annotate(qtd=Count('linha')).exclude(linha=None).order_by('-qtd')
    top_despesas = reclamacoes.exclude(terceiro__isnull=True)
    # top_despesas = reclamacoes.annotate(soma_acordos=Sum('terceiro__acordo')).annotate(despesas=Sum('terceiro__despesa__valor')).exclude(terceiro__isnull=True).order_by('-terceiro__despesa__valor')[:10]
    # top_despesas = reclamacoes.annotate(acordos=Sum('terceiro__acordo')).order_by('-acordos')
    
    from core.chart_metrics import backgrounds as bg, borders as bc, COLORS as color
    
    evolucao_reclamacoes_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    dias = 0
    for row in evolucao_reclamacoes:
        evolucao_reclamacoes_metrics['categorias'].append(f'{str(row["data"].day).zfill(2)}/{str(row["data"].month).zfill(2)}')
        evolucao_reclamacoes_metrics['dados'].append(float(row['qtd']))
        evolucao_reclamacoes_metrics['bgcolors'].append(bg.purple)
        evolucao_reclamacoes_metrics['bordercolors'].append(bc.purple)
        dias += 1
    
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
    
    
    culpabilidade = dict(NA=0, E=0, T=0)
    custo_acordos = 0
    custo_despesas = 0
    for row in reclamacoes:
        custo_acordos += row.acordos()
        custo_despesas += row.despesas()
        if row.culpabilidade != '':
            culpabilidade[row.culpabilidade] += 1
        else:
            culpabilidade['NA'] += 1
    
    metrics = {
        'periodo_de': periodo_de if isinstance(periodo_de, date) else datetime.strptime(periodo_de, '%Y-%m-%d'),
        'periodo_ate': periodo_ate if isinstance(periodo_ate, date) else datetime.strptime(periodo_ate, '%Y-%m-%d'),
        'qtd_reclamacoes': reclamacoes.count(),
        'top_despesas': top_despesas,
        'custo_acordos': custo_acordos,
        'custo_despesas': custo_despesas,
        'culpabilidade':culpabilidade,
        'empresa_nome':empresa_nome,
        'evolucao_reclamacoes':evolucao_reclamacoes_metrics,
        'reclamacoes_classificacao':reclamacoes_classificacao_metrics,
        'reclamacoes_empresa':reclamacoes_empresa_metrics,
        'reclamacoes_linha':reclamacoes_linha_metrics,
    }
    metrics['custo_total'] = metrics['custo_acordos'] + metrics['custo_despesas']
    return render(request, 'sac/reclamacao_dashboard.html', {'metrics': metrics})