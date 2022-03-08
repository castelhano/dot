from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Frota, Componente
from core.models import Empresa
from datetime import date, datetime, timedelta
from django.db.models import F
from core.chart_metrics import backgrounds as bg, borders as bc, MONTH_ABBR as m, COLORS as color
from django.db.models.functions import TruncYear
from django.db.models import Sum, Count

@login_required
@permission_required('oficina.dashboard_frota')
def frota_dashboard(request):
    if request.GET.get('data_simulada', None):
        data_simulada = datetime.strptime(request.GET.get('data_simulada', None), '%Y-%m-%d').date()
    else:
        data_simulada = date.today()
    frota = Frota.objects.all().exclude(status__in=['V', 'I']).order_by('prefixo')
    
    if request.GET.get('empresa', None):
        try:
            if request.user.is_superuser:
                empresa = Empresa.objects.get(id=request.GET.get('empresa', None))
            else:
                empresa = request.user.profile.empresas.filter(id=request.GET.get('empresa', None)).get()
        except:
            messages.error(request,'Empresa <b>não encontrada</b> ou <b>não habilitada</b> para o seu usuário')
            return redirect('oficina_frota_dashboard')
        frota = frota.filter(empresa=empresa)
    else:
        if not request.user.is_superuser:
            frota = frota.filter(empresa__in=request.user.profile.empresas.all())
        
    componentes = Componente.objects.filter(frota_componentes__in=frota).annotate(qtde=Count('nome')).order_by('nome')
    componentes_metrics = {}
    for row in componentes:
        componentes_metrics[row.nome] = row.qtde
    
    if not request.GET.get('resumo_por', None) or request.GET.get('resumo_por', None) == 'aniversario':
        frota_idade = frota.exclude(aniversario=None).annotate(ano=TruncYear('aniversario')).values('ano').annotate(total=Count('ano')).order_by()
    elif request.GET.get('resumo_por', None) == 'ano_fabricacao':
        frota_idade = frota.exclude(ano_fabricacao=None).annotate(ano=F('ano_fabricacao')).values('ano').annotate(total=Count('ano')).order_by()
    elif request.GET.get('resumo_por', None) == 'ano_modelo':
        frota_idade = frota.exclude(ano_modelo=None).annotate(ano=F('ano_modelo')).values('ano').annotate(total=Count('ano')).order_by()
    else:
        messages.error(request,'Opção de resumo <b>inválida</b>')
    
    frota_idade_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    
    
    soma_idade_frota = 0
    qtde_idade_frota = 0
    idade_frota_ignorada = []
    modelo_frota_ignorada = []
    marcas = dict()
    marcas_sum = dict()
    for f in frota: # Percore a frota para calculo da idade media e resumo das marcas e modelos
        if f.modelo: # Verifica se o modelo do carro foi preenchido
            if f.modelo.marca.nome in marcas: # Verifica se ja existe entrada para marca no dicionario de marcas
                marcas_sum[f.modelo.marca.nome] += 1
                if f.modelo.nome in marcas[f.modelo.marca.nome]:
                    marcas[f.modelo.marca.nome][f.modelo.nome] += 1
                else:
                    marcas[f.modelo.marca.nome][f.modelo.nome] = 1                    
            else:
                marcas_sum[f.modelo.marca.nome] = 1
                marcas[f.modelo.marca.nome] = {f.modelo.nome:1}
        else:
            modelo_frota_ignorada.append(f.prefixo)
        # *********************************************** 
        if request.GET.get('resumo_por', None) == 'ano_fabricacao' and f.ano_fabricacao:
            soma_idade_frota += f.idade_ano_fabricacao(data_simulada)
            qtde_idade_frota += 1
        elif request.GET.get('resumo_por', None) == 'ano_modelo' and f.ano_modelo:
            soma_idade_frota += f.idade_ano_modelo(data_simulada)
            qtde_idade_frota += 1
        elif (not request.GET.get('resumo_por', None) or request.GET.get('resumo_por', None) == 'aniversario') and f.aniversario:
            soma_idade_frota += f.idade_aniversario(data_simulada)
            qtde_idade_frota += 1
        else:
            idade_frota_ignorada.append(f.prefixo)
    
    for row in frota_idade: # Percorre frota para preencher frota por ano (para grafico)
        frota_idade_metrics['categorias'].append(row['ano'].year if request.GET.get('resumo_por', None) in ['aniversario', None] else row['ano'])
        frota_idade_metrics['dados'].append(float(row['total']))
        frota_idade_metrics['bgcolors'].append(bg.success)
        frota_idade_metrics['bordercolors'].append(bc.success)
    metrics = {
        'data_simulada':data_simulada,
        'empresa_nome':'Todas' if not request.GET.get('empresa', None) else empresa.nome,
        'resumo_por_display':request.GET.get('resumo_por', None).replace('_', ' ').title() if request.GET.get('resumo_por', None) else 'Aniversario',
        'frota_ativa':frota.count(),
        'frota_oficina':frota.filter(status='M').count(),
        'frota_fora_operacao':frota.filter(status='F').count(),
        'frota_idade':frota_idade_metrics,
        'idade_frota_ignorada':idade_frota_ignorada,
        'modelo_frota_ignorada':modelo_frota_ignorada,
        'idade_media':soma_idade_frota / qtde_idade_frota if qtde_idade_frota > 0 else '---',
        'marcas':marcas,
        'marcas_sum':marcas_sum,
        'componentes':componentes_metrics,
    }
    metrics['frota_parada_percentual'] = round(((metrics['frota_fora_operacao'] + metrics['frota_oficina']) / metrics['frota_ativa']) * 100) if metrics['frota_ativa'] > 0 else '---'
    
    return render(request, 'oficina/frota_dashboard.html', {'metrics':metrics})