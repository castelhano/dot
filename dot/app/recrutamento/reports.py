from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Candidato, Selecao
from pessoal.models import Cargo
from datetime import date, datetime, timedelta
from django.db.models.functions import TruncMonth
from django.db.models import Sum, Count

@login_required
@permission_required('recrutamento.view_candidato')
def candidato_dashboard(request):
    if request.GET.get('periodo_analise_dias', None) != 'all':
        periodo_analise_dias = int(request.GET.get('periodo_analise_dias', 365))
        until = datetime.now() - timedelta(days=periodo_analise_dias)
        candidatos = Candidato.objects.filter(create_at__gte=until)
        selecoes = Selecao.objects.filter(data__gte=until)
    else:
        periodo_analise_dias = 'all'
        candidatos = Candidato.objects.all()        
        selecoes = Selecao.objects.all()
    
    cargo = request.GET.get('cargo', None)
    if cargo:
        candidatos = candidatos.filter(vagas__cargo__id=cargo)
        selecoes = selecoes.filter(vaga__cargo__id=cargo)
        cargo = Cargo.objects.get(id=request.GET['cargo'])
    
    evolucao_banco = candidatos.annotate(mes=TruncMonth('create_at')).values('mes').annotate(total=Count('mes'))
    
    from core.chart_metrics import backgrounds as bg, borders as bc, MONTH_ABBR as m, COLORS as color
    evolucao_banco_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    for row in evolucao_banco:
        evolucao_banco_metrics['categorias'].append(m[row['mes'].month] + ' ' + str(row['mes'].year)[2:4])
        evolucao_banco_metrics['dados'].append(float(row['total']))
        evolucao_banco_metrics['bgcolors'].append(bg.purple)
        evolucao_banco_metrics['bordercolors'].append(bc.purple)
    
    soma_idade = 0
    quantidade_candidatos = 0
    for c in candidatos: # Percorre candidatos para calcular a media de idade
        if c.data_nascimento:
            soma_idade += c.idade()
            quantidade_candidatos += 1
    
    criterios_reprovados = {}
    total_criterios = 0
    for s in selecoes: # Cria resumo de criterios que mais reprovaram no periodo
        for c in s.avaliacoes().filter(status='R'):
            if c.criterio.nome in criterios_reprovados:
                criterios_reprovados[c.criterio.nome] += 1
            else:
                criterios_reprovados[c.criterio.nome] = 1
            total_criterios += 1
    
    sorted_criterios_reprovados = sorted_dict = dict(sorted(criterios_reprovados.items(), key=lambda item: item[1], reverse=True))
    
    metrics = {
        'periodo_analise_dias': int(periodo_analise_dias / 30) if periodo_analise_dias != 'all' else '---',
        'cargo_nome': cargo.nome if cargo else None,
        'cadastros_banco': candidatos.count(),
        'processos_seletivos': selecoes.count(),
        'contratacoes_periodo': candidatos.filter(status='C').count(),
        'contratacoes_mulheres': candidatos.filter(status='C', sexo='F').count(),
        'contratacoes_pne': candidatos.filter(status='C', pne=True).count(),
        'media_idade': round(soma_idade / quantidade_candidatos) if quantidade_candidatos > 0 else '--',
        'cadastros_site': candidatos.filter(origem='S').count(),
        'criterios_reprovados':sorted_criterios_reprovados,
        'total_criterios':total_criterios,
        'evolucao_banco':evolucao_banco_metrics,
    }
    metrics['percentual_aprovacoes'] = round(selecoes.filter(resultado='A').count() / metrics['processos_seletivos'] * 100, 2) if metrics['processos_seletivos'] > 0 else '---'
    metrics['percentual_contratacao_mulheres'] = round(metrics['contratacoes_mulheres'] / metrics['contratacoes_periodo'] * 100, 2) if metrics['contratacoes_periodo'] > 0 else '---'
    metrics['percentual_contratacao_pne'] = round(metrics['contratacoes_pne'] / metrics['contratacoes_periodo'] * 100, 2) if metrics['contratacoes_periodo'] > 0 else '---'
    metrics['percentual_cadastros_site'] = round(metrics['cadastros_site'] / metrics['cadastros_banco'] * 100, 2) if metrics['cadastros_banco'] > 0 else '---'
    return render(request, 'recrutamento/candidato_dashboard.html', {'metrics': metrics})