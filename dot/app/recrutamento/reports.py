# from django.http import HttpResponse
# from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from .models import Candidato, Selecao, Avaliacao, Vaga
from pessoal.models import Cargo
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum

@login_required
@permission_required('recrutamento.dashboard_recrutamento')
def candidato_dashboard(request):
    if request.GET.get('periodo_analise_dias', None) != 'all':
        periodo_analise_dias = int(request.GET.get('periodo_analise_dias', 365))
        until = datetime.now() - timedelta(days=periodo_analise_dias)
        candidatos = Candidato.objects.filter(create_at__gte=until)
        selecoes = Selecao.objects.filter(data__gte=until)
        criterios_reprovados = Avaliacao.objects.filter(selecao__data__gte=until, status='R')
    else:
        periodo_analise_dias = 'all'
        candidatos = Candidato.objects.all()        
        selecoes = Selecao.objects.all()
        criterios_reprovados = Avaliacao.objects.filter(status='R')
    
    vaga = Vaga.objects.get(id=request.GET['vaga']) if request.GET.get('vaga', None) else None
    if vaga:
        # cargo = Cargo.objects.get(id=request.GET['cargo'])
        candidatos = candidatos.filter(vagas__cargo=vaga.cargo)
        selecoes = selecoes.filter(vaga__cargo=vaga.cargo)
        criterios_reprovados = criterios_reprovados.filter(status='R', selecao__vaga__cargo=vaga.cargo)
    
    # evolucao_banco = candidatos.annotate(mes=TruncMonth('create_at')).values('mes').annotate(total=Count('mes'))
    evolucao_selecoes = selecoes.annotate(mes=TruncMonth('data')).values('mes').annotate(total=Count('mes'))
    total_avaliacoes = criterios_reprovados.count()
    criterios_reprovados = criterios_reprovados.values('criterio__nome').annotate(qtd=Count('criterio__nome'))
    
    from core.chart_metrics import backgrounds as bg, borders as bc, MONTH_ABBR as m, COLORS as color
    evolucao_selecoes_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    for row in evolucao_selecoes:
        evolucao_selecoes_metrics['categorias'].append(m[row['mes'].month] + ' ' + str(row['mes'].year)[2:4])
        evolucao_selecoes_metrics['dados'].append(float(row['total']))
        evolucao_selecoes_metrics['bgcolors'].append(bg.purple)
        evolucao_selecoes_metrics['bordercolors'].append(bc.purple)
    
    soma_idade = 0
    quantidade_candidatos = 0
    for c in candidatos: # Percorre candidatos para calcular a media de idade
        if c.data_nascimento:
            soma_idade += c.idade()
            quantidade_candidatos += 1
    
    metrics = {
        'periodo_analise_dias': int(periodo_analise_dias / 30) if periodo_analise_dias != 'all' else '---',
        'cargo_nome': vaga.cargo.nome if vaga else None,
        'cadastros_banco': candidatos.count(),
        'processos_seletivos': selecoes.count(),
        'contratacoes_periodo': candidatos.filter(status='C').count(),
        'candidatos_mulheres': candidatos.filter(sexo='F').count(),
        'saldo_banco': Vaga.objects.all().exclude(candidatos__isnull=True),
        'banco_totalizado': Vaga.objects.filter(candidatos__status='B').count(),
        'candidatos_pne': candidatos.filter(pne=True).count(),
        'media_idade': round(soma_idade / quantidade_candidatos) if quantidade_candidatos > 0 else '--',
        'cadastros_site': candidatos.filter(origem='S').count(),
        'criterios_reprovados':criterios_reprovados,
        'total_avaliacoes':total_avaliacoes,
        'evolucao_selecoes':evolucao_selecoes_metrics,
    }
    metrics['percentual_aprovacoes'] = selecoes.filter(resultado='A').count() / metrics['processos_seletivos'] * 100 if metrics['processos_seletivos'] > 0 else 0
    return render(request, 'recrutamento/candidato_dashboard.html', {'metrics': metrics})