from django.http import HttpResponse
import json
from core.md_report import md_report
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Acidente, Terceiro, Termo
from core.models import Empresa
from datetime import date, datetime
from django.db.models import Count


@login_required
@permission_required('sinistro.view_acidente', login_url="/handler/403")
def capa_resumo(request):
    acidente = Acidente.objects.get(pk=request.GET['acidente'])
    empresa = acidente.empresa
    terceiros = Terceiro.objects.filter(acidente=acidente)
    terceiros_txt = ''
    for terceiro in terceiros:
        terceiros_txt += f'[...]==**{terceiro.get_classificacao_display()}**== **{terceiro.veiculo}** {terceiro.nome} | Acordo: =-{locale.currency(terceiro.acordo, grouping=True)}-=<br />'
    schema = """##_ RELATÓRIO DE CONCLUSÃO DE OCORRÊNCIA OPERACIONAL<br /><br />

Culpabilidade: **$(acidente.get_culpabilidade_display)**<br />Classificação: **$(acidente.classificacao.nome)**<br />Data: **%s**<br />Hora: **%s**<br />Condutor: **$(acidente.condutor.matricula) - $(acidente.condutor.nome)**<br />Inspetor: **$(acidente.inspetor.matricula) - $(acidente.inspetor.nome)**
**Terceiros:**<br />%s

[[ %s ]]<br /><br />
--
<br /><br />
### RESUMO DOS CUSTOS DO PROCESSO<br />
Acordos: **%s**<br />Outras despesas: **%s**<br />....................................
**Custo Total: %s**
![105,45,TOP-LEFT]()
[footer][/footer]""" %(acidente.data.strftime('%d/%m/%Y') if acidente.data else '', acidente.hora.strftime("%H:%M") if acidente.hora else '', terceiros_txt,acidente.detalhe.replace('\n','<br />') ,locale.currency(acidente.acordos(), grouping=True),locale.currency(acidente.despesas(), grouping=True), locale.currency(acidente.acordos() + acidente.despesas(), grouping=True))
    try:
        pdf = md_report(request, schema, **{"acidente":acidente,"empresa":empresa})
    except:
        messages.error(request, '<b>ERRO</b> ao gerar capa, procure o administrador do sistema')
        return redirect('sinistro_acidente_id', acidente.id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="capa.pdf"'
    response.write(pdf)
    return response


@login_required
@permission_required('sinistro.view_termo', login_url="/handler/403")
def termo_pdf(request):
    termo = Termo.objects.get(pk=request.GET['termo'])
    terceiro = Terceiro.objects.get(pk=request.GET['terceiro'])
    acidente = terceiro.acidente
    empresa = terceiro.acidente.empresa
    try:
        pdf = md_report(request, termo.body, **{"acidente":acidente,"terceiro":terceiro,"empresa":empresa})
    except:
        messages.error(request, '<b>ERRO:</b> Termo mal formatado, revise a extrutura do documento.')
        return redirect('sinistro_terceiro_id', terceiro.id)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="termo.pdf"'
    response.write(pdf)
    return response



@login_required
@permission_required('sinistro.change_termo', login_url="/handler/403")
def termo_modelos(request):
    modelos = []
    md1 = """# Titulo
Texto de exemplo em **negrito** *italico* ou ==destaque==
--
> Paragrafo destacado

Nome terceiro: **$(terceiro.nome)**

[[ Caixa de destaque]]

Saldo é de =+R$ 222,35+= e o débito será de =-R$ -1.254,33-=
___ Texto a direita"""
    md2 = """##_ TERMO DE COMPOSIÇÃO AMIGÁVEL QUE ENTRE SI FAZEM

De um lado, como primeiro acordante temos, **$(empresa.razao_social)** pessoa jurídica de direito privado, estabelecida na **$(empresa.endereco)** - bairro **$(empresa.bairro)** - CEP: **$(empresa.cep)**, **$(empresa.cidade) $(empresa.uf)**, incrita no CNPJ/MF **$(empresa.cnpj)**,
e, segundo acordante, **$(terceiro.nome)**, portador do CPF: **$(terceiro.cpf)**, residente e domiciliado à **$(terceiro.endereco)**, bairro **$(terceiro.bairro)** em **$(terceiro.cidade)** **$(terceiro.uf)**.

**Dos Fatos**<br />O presente termo é lavrado ante a ocorrência de colisão entre o veículo ônibus de prefixo **$(acidente.veiculo)**, placa **$(acidente.veiculo.placa)**, e o veículo de propriedade do segundo acordante, cuja marca/modelo se descreve: **$(terceiro.veiculo)**, cor **$(terceiro.cor)**, ano **$(terceiro.ano)**, placa **$(terceiro.placa)** - sendo o local do acidente ocorrido em **$(acidente.endereco)**, **$(acidente.bairro)**, **$(acidente.cidade) $(acidente.uf)**, na data de **$(acidente.data)**, aproximadamente às **$(acidente.hora)**<br />

A empresa citada pagará o montante de **$(terceiro.acordo)** em **$(terceiro.forma)**, referente aos danos ocorridos no veículo do segundo acordante, conforme dados constantes do PIA nº **$(acidente.pasta)** (processo interno de acidentes), e que o valor acima pago refere-se à composição amigável entre as partes, no tocante ao sinistro em apreço.<br />

**O pagamento efetuado pela empresa não acarreta reconhecimento de culpa sendo ato meramente liberal e ainda, com o pagamento acima descrito, o segundo acordante conferirá à primeira acordante a mais ampla, geral e irrevogável quitação quanto aos danos morais, materiais e lucros cessantes ou a que título for que tenha como objeto o fato descrito no presente termo.**

Por estarem as partes de comum acordo, assinam.
[signature] {Representante, $(empresa.razao_social)};{$(terceiro.nome), $(terceiro.cpf)}[/signature]
![105,45,TOP-LEFT]()
[footer][/footer]
"""
    modelos.append({"name":"Exemplo","body":md1})
    modelos.append({"name":"Composicao","body":md2})
    obj = json.dumps(modelos)
    return HttpResponse(obj, content_type="application/json")

@login_required
@permission_required('sinistro.dashboard_acidente', login_url="/handler/403")
def acidente_dashboard(request):
    periodo_de = request.GET.get('periodo_de', date.today().replace(day=1))
    periodo_ate = request.GET.get('periodo_ate', date.today())
    acidentes = Acidente.objects.filter(data__range=[periodo_de,periodo_ate])
    
    if request.GET.get('empresa', None):
        try:
            if request.user.is_superuser:
                empresa = Empresa.objects.get(id=request.GET.get('empresa', None))
            else:
                empresa = request.user.profile.empresas.filter(id=request.GET.get('empresa', None)).get()
            empresa_nome = empresa.nome
        except:
            messages.error(request,'Empresa <b>não encontrada</b> ou <b>não habilitada</b> para o seu usuário')
            return redirect('sinistro_acidente_dashboard')
        acidentes = acidentes.filter(empresa=empresa)
    else:
        if not request.user.is_superuser:
            acidentes = acidentes.filter(empresa__in=request.user.profile.empresas.all())
        empresa_nome = None
    evolucao_acidentes = acidentes.values('data').annotate(qtd=Count('data')).order_by()
    acidentes_empresa = acidentes.values('empresa__nome').annotate(qtd=Count('empresa')).order_by()
    acidentes_classificacao = acidentes.values('classificacao__nome').annotate(qtd=Count('classificacao')).exclude(classificacao=None).order_by('-qtd')
    acidentes_linha = acidentes.values('linha__codigo').annotate(qtd=Count('linha')).exclude(linha=None).order_by('-qtd')
    top_despesas = acidentes.exclude(terceiro__isnull=True)
    
    from core.chart_metrics import backgrounds as bg, borders as bc, COLORS as color
    
    evolucao_acidentes_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    dias = 0
    for row in evolucao_acidentes:
        evolucao_acidentes_metrics['categorias'].append(f'{str(row["data"].day).zfill(2)}/{str(row["data"].month).zfill(2)}')
        evolucao_acidentes_metrics['dados'].append(float(row['qtd']))
        evolucao_acidentes_metrics['bgcolors'].append(bg.purple)
        evolucao_acidentes_metrics['bordercolors'].append(bc.purple)
        dias += 1
    
    acidentes_empresa_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    for step, row in enumerate(acidentes_empresa):
        acidentes_empresa_metrics['categorias'].append(row['empresa__nome'])
        acidentes_empresa_metrics['dados'].append(int(row['qtd']))
        acidentes_empresa_metrics['bgcolors'].append(color[step])
        acidentes_empresa_metrics['bordercolors'].append(color[step])
    
    acidentes_classificacao_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    for row in acidentes_classificacao:
        acidentes_classificacao_metrics['categorias'].append(row['classificacao__nome'])
        acidentes_classificacao_metrics['dados'].append(int(row['qtd']))
        acidentes_classificacao_metrics['bgcolors'].append(bg.purple)
        acidentes_classificacao_metrics['bordercolors'].append(bc.purple)
    
    acidentes_linha_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    for row in acidentes_linha:
        acidentes_linha_metrics['categorias'].append(row['linha__codigo'])
        acidentes_linha_metrics['dados'].append(int(row['qtd']))
        acidentes_linha_metrics['bgcolors'].append(bg.purple)
        acidentes_linha_metrics['bordercolors'].append(bc.purple)
    
    
    culpabilidade = dict(NA=0, E=0, T=0)
    custo_acordos = 0
    custo_despesas = 0
    for row in acidentes:
        custo_acordos += row.acordos()
        custo_despesas += row.despesas()
        if row.culpabilidade != '':
            culpabilidade[row.culpabilidade] += 1
        else:
            culpabilidade['NA'] += 1
    
    metrics = {
        'periodo_de': periodo_de if isinstance(periodo_de, date) else datetime.strptime(periodo_de, '%Y-%m-%d'),
        'periodo_ate': periodo_ate if isinstance(periodo_ate, date) else datetime.strptime(periodo_ate, '%Y-%m-%d'),
        'qtd_acidentes': acidentes.count(),
        'top_despesas': top_despesas,
        'custo_acordos': custo_acordos,
        'custo_despesas': custo_despesas,
        'culpabilidade':culpabilidade,
        'empresa_nome':empresa_nome,
        'evolucao_acidentes':evolucao_acidentes_metrics,
        'acidentes_classificacao':acidentes_classificacao_metrics,
        'acidentes_empresa':acidentes_empresa_metrics,
        'acidentes_linha':acidentes_linha_metrics,
    }
    metrics['custo_total'] = metrics['custo_acordos'] + metrics['custo_despesas']
    return render(request, 'sinistro/acidente_dashboard.html', {'metrics': metrics})