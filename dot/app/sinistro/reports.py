import csv
from django.http import HttpResponse

# IMPORTS PARA REPORTLAB
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Frame, PageTemplate
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.styles import ParagraphStyle
import locale
locale.setlocale(locale.LC_ALL, '')

# OUTROS IMPORTS
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Acidente, Terceiro, Despesa, Termo, Paragrafo
from core.models import Empresa, Log
from datetime import date, datetime
# from django.db.models.functions import TruncMonth
from django.db.models import Count, Sum


@login_required
@permission_required('sinistro.view_acidente')
def capa_resumo(request):
    acidente = Acidente.objects.get(pk=request.GET['acidente'])
    
    buffer = BytesIO()
    PAGE_WIDTH  = A4[0]
    PAGE_HEIGHT = A4[1]
    MX = 30
    MY = 45
    doc = SimpleDocTemplate(buffer,topMargin=MY,bottomMargin=MY,leftMargin=MX,rightMargin=MX)
    
    LEFT = 0
    CENTER = 1
    RIGHT = 2
    JUSTIFY = 4
    
    titulo_style = ParagraphStyle(
        name='Normal',
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=CENTER,
        spaceAfter=208
    )
    indice_style = ParagraphStyle(
        name='Normal',
        fontName='Helvetica',
        fontSize=12,
        alignment=LEFT
    )
    info_style = ParagraphStyle(
        name='Normal',
        fontName='Helvetica-Bold',
        fontSize=12,
        alignment=LEFT
    )
    paragrafo_style = ParagraphStyle(
        name='Normal',
        fontName='Helvetica',
        fontSize=10,
        alignment=JUSTIFY,
        leftIndent = 25,
        rightIndent = 25
    )
    empresa_style = ParagraphStyle(
        name='Normal',
        fontName='Helvetica-Bold',
        fontSize=9,
        alignment=CENTER
    )
    rodape_style = ParagraphStyle(
        name='Normal',
        fontName='Helvetica',
        fontSize=9,
        alignment=CENTER
    )
    
    # RESUMO, ASSINATURA e RODAPE
    def basic_template(canvas, doc):
        canvas.saveState()
        
        
        # INFORMAÇÕES SOBRE SINISTRO
        info_start = 145
        
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(doc.width - 30,720, 'PASTA')
        canvas.setFont("Helvetica-Bold", 20)
        pasta_size = stringWidth(acidente.pasta,"Helvetica-Bold", 16)
        canvas.drawString(doc.width - (pasta_size / 2) - 12,700, acidente.pasta)
        
        indice_size = stringWidth('CULPABILIDADE:',"Helvetica", 9)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 9)
        canvas.drawString(indice_start,720,'CULPABILIDADE:')
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(info_start,720, acidente.get_culpabilidade_display().upper())
        
        indice_size = stringWidth('CLASSIFICAÇÃO:',"Helvetica", 9)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 9)
        canvas.drawString(indice_start,705,'CLASSIFICAÇÃO:')
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(info_start,705, acidente.classificacao.nome.upper() if acidente.classificacao != None else '')
        
        indice_size = stringWidth('DATA:',"Helvetica", 9)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 9)
        canvas.drawString(indice_start,690,'DATA:')
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(info_start,690, acidente.data.strftime("%d/%m/%Y"))
        
        indice_size = stringWidth('HORA:',"Helvetica", 9)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 9)
        canvas.drawString(indice_start,675,'HORA:')
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(info_start,675, acidente.hora.strftime("%H:%M") if acidente.hora != None else '')
        
        indice_size = stringWidth('VEICULO:',"Helvetica", 9)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 9)
        canvas.drawString(indice_start,660,'VEICULO:')
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(info_start,660, acidente.veiculo.prefixo if acidente.veiculo != None else '')
        
        indice_start = 200
        canvas.setFont("Helvetica", 9)
        canvas.drawString(indice_start,660,'PLACA:')
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(info_start + 90,660, acidente.veiculo.placa if acidente.veiculo != None else '')
        
        indice_size = stringWidth('LINHA:',"Helvetica", 9)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 9)
        canvas.drawString(indice_start,645,'LINHA:')
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(info_start,645, acidente.linha.codigo + ' - ' + acidente.linha.nome if acidente.linha != None else '')
        
        indice_size = stringWidth('LOCAL:',"Helvetica", 9)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 9)
        canvas.drawString(indice_start,630,'LOCAL:')
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(info_start,630, acidente.endereco + ', ' + acidente.bairro + ', ' + acidente.cidade + '-' + acidente.uf)
        
        indice_size = stringWidth('CONDUTOR:',"Helvetica", 9)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 9)
        canvas.drawString(indice_start,615,'CONDUTOR:')
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(info_start,615, acidente.condutor.matricula + ' - ' + acidente.condutor.nome if acidente.condutor else '')
        
        indice_size = stringWidth('INSPETOR:',"Helvetica", 9)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 9)
        canvas.drawString(indice_start,600,'INSPETOR:')
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(info_start,600, acidente.inspetor.matricula + ' - ' + acidente.inspetor.nome if acidente.inspetor else '')
        
        # DETALHAMENTO ACIDENTE
        canvas.setDash(1,2)
        canvas.setLineWidth(0)
        canvas.line(MX + 30,580, PAGE_WIDTH - 60,585)
        
        P = Paragraph(acidente.detalhe.replace('\n','<br />'), paragrafo_style)
        flowables.append(P)
        
        canvas.line(MX + 30,450, PAGE_WIDTH - 60,450)
        
        # RESUMO DOS CUSTOS / DESPESAS DO SINISTRO
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(60 ,410,'RESUMO DOS CUSTOS DO PROCESSO:')
        
        indice_size = stringWidth('ACORDOS:',"Helvetica", 9)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 9)
        canvas.drawString(indice_start,385,'ACORDOS:')
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(info_start,385, 'R$ ' + '{:_.2f}'.format(acidente.acordos()).replace('.',',').replace('_','.'))
        
        indice_size = stringWidth('OUTRAS DESPESAS:',"Helvetica", 9)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 9)
        canvas.drawString(indice_start,370,'OUTRAS DESPESAS:')
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(info_start,370, 'R$ ' + '{:_.2f}'.format(acidente.despesas()).replace('.',',').replace('_','.'))
        
        # canvas.setLineWidth(1)
        canvas.line(MX + 40,360,210,360)
        
        indice_size = stringWidth('CUSTO TOTAL:',"Helvetica-Bold", 9)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(indice_start,345,'CUSTO TOTAL:')
        canvas.drawString(info_start,345, 'R$ ' + '{:_.2f}'.format(acidente.acordos() + acidente.despesas()).replace('.',',').replace('_','.'))
        
        
        # ESCREVENDO ASSINATURAS
        canvas.setDash(1)
        canvas.setLineWidth(1)
        canvas.line(MX,135,(PAGE_WIDTH / 2)- 10,135)
        canvas.line(PAGE_WIDTH-(PAGE_WIDTH / 2 - 10),135,PAGE_WIDTH - MX,135)
        canvas.setFont("Helvetica-Bold", 9)
        
        sinistro_size = stringWidth('DPTO SINISTRO',"Helvetica-Bold", 9)
        gerencia_size = stringWidth('GERÊNCIA',"Helvetica-Bold", 9)
        
        sinistro_start = ((PAGE_WIDTH / 2) - sinistro_size) / 2 + 10
        gerencia_start = (PAGE_WIDTH / 2) + (((PAGE_WIDTH / 2 - gerencia_size) / 2) - 10)
        
        canvas.drawString(sinistro_start,120,'DPTO SINISTRO')
        canvas.drawString(gerencia_start,120,'GERÊNCIA')
        
        # ESCREVENDO RODAPE
        rodape_empresa = acidente.empresa.razao_social
        rodape_l1 = acidente.empresa.endereco + ' Bairro ' + acidente.empresa.bairro + ' ' + acidente.empresa.cidade + '-' + acidente.empresa.uf
        rodape_l2 = 'CEP ' + acidente.empresa.cep + ' | ' + 'CNPJ: ' + acidente.empresa.cnpj
        
        P = Paragraph(rodape_empresa,empresa_style)
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.leftMargin, h+34)
        
        P = Paragraph(rodape_l1,rodape_style)
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.leftMargin, h+20)
        
        P = Paragraph(rodape_l2,rodape_style)
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.leftMargin, h+8)
        
        # ADICIONANDO LINHA RODAPE
        canvas.setLineWidth(0)
        canvas.setStrokeColorRGB(155/256,155/256,155/256)
        canvas.line(30,62,PAGE_WIDTH-30,62)
        canvas.restoreState()
    
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,id='frame')
    template = PageTemplate(id='capa', frames=frame, onPage=basic_template)
    doc.addPageTemplates([template])
    
    flowables = []
    
    # TITULO
    titulo = '\nRELATÓRIO DE CONCLUSÃO DE OCORRÊNCIA OPERACIONAL'
    flowables.append(Paragraph(titulo,titulo_style))

    
    doc.build(flowables)
    pdf_value = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="capa.pdf"'
    
    response.write(pdf_value)
    return response

# ------------------------------------------------------------------------------------------------

@login_required
@permission_required('sinistro.view_termo')
def termo_pdf(request):
    acidente = Acidente.objects.get(pk=request.GET['acidente'])
    terceiro = Terceiro.objects.get(pk=request.GET['terceiro'])
    termo = Termo.objects.get(pk=request.GET['termo'])
    paragrafos = Paragrafo.objects.filter(termo=termo).order_by('ordem')
        
    fields = {
        '\n':'<br/>',
        '{{':'<b>',
        '}}':'</b>',
        '[[':'<u>',
        ']]':'</u>',
        '((':'<i>',
        '))':'</i>',
        '__-':'<strike>',
        '-__':'</strike>',
        '*->':'&bull;',
        'empresa.nome':acidente.empresa.nome.upper() if acidente.empresa != None else '',
        'empresa.razao_social':acidente.empresa.razao_social.upper() if acidente.empresa != None else '',
        'empresa.cnpj':acidente.empresa.cnpj if acidente.empresa != None else '',
        'empresa.endereco':acidente.empresa.endereco.upper() if acidente.empresa != None else '',
        'empresa.cidade':acidente.empresa.cidade.upper() if acidente.empresa != None else '',
        'empresa.uf':acidente.empresa.uf.upper() if acidente.empresa != None else '',
        'empresa.bairro':acidente.empresa.bairro.upper() if acidente.empresa != None else '',
        'empresa.cep':acidente.empresa.cep if acidente.empresa != None else '',
        'acidente.pasta':acidente.pasta if acidente.pasta != None else '',
        'acidente.data':acidente.data.strftime("%d/%m/%Y") if acidente.data != None else '',
        'acidente.hora':acidente.hora.strftime("%H:%M") if acidente.hora != None else '',
        'acidente.classificacao':acidente.classificacao.nome if acidente.classificacao != None else '',
        'acidente.culpabilidade':acidente.get_culpabilidade_display().upper(),
        'acidente.veiculo':acidente.veiculo,
        'veiculo.placa':acidente.veiculo.placa.upper() if acidente.veiculo != None else '',
        'acidente.condutor':acidente.condutor,
        'condutor.nome':acidente.condutor.nome.upper() if acidente.condutor != None else '',
        'acidente.inspetor':acidente.inspetor,
        'inspetor.nome':acidente.inspetor.nome.upper() if acidente.inspetor != None else '',
        'acidente.linha':acidente.linha.codigo if acidente.linha != None else '',
        'acidente.linha.nome':acidente.linha.nome.upper() if acidente.linha != None else '',
        'acidente.endereco':acidente.endereco.upper(),
        'acidente.bairro':acidente.bairro.upper(),
        'acidente.cidade':acidente.cidade.upper(),
        'acidente.detalhe':acidente.detalhe,
        'acidente.uf':acidente.uf.upper(),
        'terceiro.nome':terceiro.nome.upper(),
        'terceiro.rg':terceiro.rg,
        'terceiro.cpf':terceiro.cpf,
        'terceiro.endereco':terceiro.endereco.upper(),
        'terceiro.bairro':terceiro.bairro.upper(),
        'terceiro.cidade':terceiro.cidade.upper(),
        'terceiro.uf':terceiro.uf,
        'terceiro.veiculo':terceiro.veiculo.upper(),
        'terceiro.cor':terceiro.cor.upper(),
        'terceiro.ano':terceiro.ano,
        'terceiro.placa':terceiro.placa.upper(),
        'terceiro.acordo':'{:n}'.format(terceiro.acordo),
        'terceiro.forma':terceiro.forma.nome if terceiro.forma else '',
        'terceiro.despesas':'{:n}'.format(terceiro.despesas()),
        'termo.local':termo.local.upper(),
        'termo.representante':termo.representante.upper(),
        'representante.cargo':termo.cargo.upper(),
        'oficina.nome':terceiro.oficina.nome.upper() if terceiro.oficina != None else '',
        'oficina.razao_social':terceiro.oficina.razao_social.upper() if terceiro.oficina != None else '',
        'oficina.cnpj':terceiro.oficina.cnpj if terceiro.oficina != None else '',
    }
    for item in fields:
        for paragrafo in paragrafos:
            paragrafo.texto = paragrafo.texto.replace(item,str(fields.get(item)))
        termo.titulo = termo.titulo.replace(item,str(fields.get(item)))
        termo.rodape = termo.rodape.replace(item,str(fields.get(item)))
    
    buffer = BytesIO()
    PAGE_WIDTH  = A4[0]
    PAGE_HEIGHT = A4[1]
    MX = 30
    MY = 30
    doc = SimpleDocTemplate(buffer,topMargin=MY,bottomMargin=MY,leftMargin=MX,rightMargin=MX)
    
    LEFT = 0
    CENTER = 1
    RIGHT = 2
    JUSTIFY = 4
    
    titulo_style = ParagraphStyle(
        name='Normal',
        fontName='Helvetica-Bold',
        fontSize=14,
        alignment=CENTER,
        spaceAfter=40
    )
    paragrafo_style = ParagraphStyle(
        name='Normal',
        fontName='Helvetica',
        fontSize=12,
        alignment=JUSTIFY,
        spaceAfter=20
    )
    local_style = ParagraphStyle(
        name='Normal',
        fontName='Helvetica-Bold',
        fontSize=12,
        alignment=LEFT,
        spaceAfter=20
    )
    rodape_style = ParagraphStyle(
        name='Normal',
        fontName='Helvetica',
        fontSize=7,
        alignment=CENTER
    )
    
    # LOCAL, ASSINATURA e RODAPE
    def basic_template(canvas, doc):
        canvas.saveState()
        
        # ESCREVENDO LOCAL
        local = termo.local + ', ' + date.today().strftime('%d/%m/%Y')
        P = Paragraph(local,local_style)
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.leftMargin, h+170)
        
        # ESCREVENDO ASSINATURAS
        canvas.line(MX,100,(PAGE_WIDTH / 2)- 10,100)
        canvas.line(PAGE_WIDTH-(PAGE_WIDTH / 2 - 10),100,PAGE_WIDTH - MX,100)
        canvas.setFont("Helvetica-Bold", 9)
        
        representante_size = stringWidth(termo.representante,"Helvetica-Bold", 9)
        terceiro_size = stringWidth(terceiro.nome,"Helvetica-Bold", 9)
        
        representante_start = ((PAGE_WIDTH / 2) - representante_size) / 2 + 10
        terceiro_start = (PAGE_WIDTH / 2) + (((PAGE_WIDTH / 2 - terceiro_size) / 2) - 10)
        
        canvas.drawString(representante_start,90,termo.representante.upper())
        canvas.drawString(terceiro_start,90,terceiro.nome.upper())
        
        canvas.setFont("Helvetica", 8)
        cargo_size = stringWidth(termo.cargo,"Helvetica-Bold", 8)
        cpf_size = stringWidth("CPF: 000.000.000-00","Helvetica-Bold", 8)
        cargo_start = ((PAGE_WIDTH / 2) - cargo_size) / 2 + 15
        cpf_start = (PAGE_WIDTH / 2) + (((PAGE_WIDTH / 2 - cpf_size) / 2) - 15)
        canvas.drawString(cargo_start,80,termo.cargo)
        canvas.drawString(cpf_start,80,'CPF: ' + terceiro.cpf)
        
        
        # ESCREVENDO RODAPE
        P = Paragraph(termo.rodape,rodape_style)
        w, h = P.wrap(doc.width, doc.bottomMargin)
        P.drawOn(canvas, doc.leftMargin, h+8)
        
        # ADICIONANDO LINHA RODAPE
        canvas.setLineWidth(0)
        canvas.setStrokeColorRGB(155/256,155/256,155/256)
        canvas.line(30,35,PAGE_WIDTH-30,35)
        canvas.restoreState()
    
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,id='frame')
    template = PageTemplate(id='test', frames=frame, onPage=basic_template)
    doc.addPageTemplates([template])
    
    flowables = []
    
    # TITULO
    flowables.append(Paragraph(termo.titulo.upper(),titulo_style))
    
    # PARAGRAFOS
    for paragrafo in paragrafos:
        flowables.append(Paragraph(paragrafo.texto,paragrafo_style))

    
    doc.build(flowables)
    pdf_value = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="termo.pdf"'
    
    response.write(pdf_value)
    return response

@login_required
@permission_required('sinistro.change_termo')
def termo_modelos(request, id):
    try:
        termo = Termo.objects.get(id=id)
        modelo = request.GET.get('modelo', None)
        if modelo == 'mod1' and Paragrafo.objects.filter(termo=termo).count() == 0:
            mod1 = []
            mod1.append('De um lado, como primeiro acordante temos, {{empresa.nome}} pessoa jurídica de direito privado, estabelecida na {{empresa.endereco}} - bairro {{empresa.bairro}} - CEP: {{empresa.cep}}, {{empresa.cidade}} {{empresa.uf}}, incrita no CNPJ/MF {{empresa.cnpj}},')
            mod1.append('e, segundo acordante, {{terceiro.nome}}, portador do CPF: {{terceiro.cpf}}, residente e domiciliado à {{terceiro.endereco}}, bairro {{terceiro.bairro}} em {{terceiro.cidade}} {{terceiro.uf}}.')
            mod1.append('<br />{{Dos Fatos}}<br />')
            mod1.append('O presente termo é lavrado ante a ocorrência de colisão entre o veículo ônibus de prefixo {{acidente.veiculo}}, placa {{veiculo.placa}}, e o veículo de propriedade do segundo acordante, cuja marca/modelo se descreve: {{terceiro.veiculo}}, cor {{terceiro.cor}}, ano {{terceiro.ano}}, placa {{terceiro.placa}} - sendo o local do acidente ocorrido em {{acidente.endereco}}, {{acidente.bairro}}, {{acidente.cidade}} {{acidente.uf}}, na data de {{acidente.data}}, aproximadamente às {{acidente.hora}}')
            mod1.append('A empresa citada pagará o montante de {{terceiro.acordo}} em {{terceiro.forma}}, referente aos danos ocorridos no veículo do segundo acordante, conforme dados constantes do PIA nº {{acidente.pasta}} (processo interno de acidentes), e que o valor acima pago refere-se à composição amigável entre as partes, no tocante ao sinistro em apreço.')
            mod1.append('{{O pagamento efetuado pela empresa não acarreta reconhecimento de culpa sendo ato meramente liberal e ainda, com o pagamento acima descrito, o segundo acordante conferirá à primeira acordante a mais ampla, geral e irrevogável quitação quanto aos danos morais, materiais e lucros cessantes ou a que título for que tenha como objeto o fato descrito no presente termo.}}')
            mod1.append('Por estarem às partes de comum acordo, assinam.')
            ordem = 0
            for p in mod1:
                Paragrafo.objects.create(termo=termo, ordem=ordem, texto=p)
                ordem += 1
            l = Log()
            l.modelo = "sinistro.termo"
            l.objeto_id = termo.id
            l.objeto_str = termo.nome
            l.usuario = request.user
            l.mensagem = "LOAD MODELO"
            l.save()
            messages.success(request,f'Modelo <b>{modelo}</b> aplicado')
        else:
            messages.warning(request,'Modelo <b>não localizado</b>')
    except:
        messages.error(request,'<b>Erro</b> ao carregar modelo')
    return redirect('sinistro_termo_id', id)

@login_required
@permission_required('sinistro.dashboard_acidente')
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
    # top_despesas = acidentes.annotate(soma_acordos=Sum('terceiro__acordo')).annotate(despesas=Sum('terceiro__despesa__valor')).exclude(terceiro__isnull=True).order_by('-terceiro__despesa__valor')[:10]
    # top_despesas = acidentes.annotate(acordos=Sum('terceiro__acordo')).order_by('-acordos')
    
    from core.chart_metrics import backgrounds as bg, borders as bc, COLORS as color
    
    evolucao_acidentes_metrics = {
        'categorias':[],
        'dados':[],
        'bgcolors':[],
        'bordercolors':[]
        }
    dias = 0
    for row in evolucao_acidentes:
        evolucao_acidentes_metrics['categorias'].append(row['data'].day)
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

@login_required
@permission_required('sinistro.view_acidente')
def export_acidentes_csv(request):
    try:
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="acidentes.csv"'

        writer = csv.writer(response, delimiter =';')
        writer.writerow(['#','Empresa','Pasta','Classificacao','Data','Hora','Veiculo','Linha','Nome linha','Condutor','Nome condutor','Inspetor','Nome inspetor','Endereco','Bairro','Cidade','UF','Culpabilidade','Concluido','Terceiro','CPF','Veiculo Terceiro','Placa','Cor','Ano','Forma','Oficina','Acordo','Despesas','Custo Total'])
        
        periodo_de = request.GET.get('periodo_de', date.today().replace(day=1))
        periodo_ate = request.GET.get('periodo_ate', date.today())
        acidentes = Acidente.objects.filter(data__range=[periodo_de,periodo_ate])
        terceiros = Terceiro.objects.filter(acidente__data__range=[periodo_de,periodo_ate])
        
        if request.GET.get('empresa', None):
            try:
                if request.user.is_superuser:
                    empresa = Empresa.objects.get(id=request.GET.get('empresa', None))
                else:
                    empresa = request.user.profile.empresas.filter(id=request.GET.get('empresa', None)).get()
            except:
                messages.error(request,'Empresa <b>não encontrada</b> ou <b>não habilitada</b> para o seu usuário')
                return redirect('sinistro_acidentes')
            acidentes = acidentes.filter(empresa=empresa)
            terceiros = terceiros.filter(empresa=empresa)
        else:
            if not request.user.is_superuser:
                acidentes = acidentes.filter(empresa__in=request.user.profile.empresas.all())
        
        acidentes = acidentes.filter(terceiro__isnull=True).values_list('id','empresa__nome','pasta','classificacao__nome','data','hora','veiculo__prefixo','linha__codigo','linha__nome','condutor__matricula','condutor__nome','inspetor__matricula','inspetor__nome','endereco','bairro','cidade','uf','culpabilidade','concluido')
        terceiros = terceiros.values_list('acidente__id','acidente__empresa__nome','acidente__pasta','acidente__classificacao__nome','acidente__data','acidente__hora','acidente__veiculo__prefixo','acidente__linha__codigo','acidente__linha__nome','acidente__condutor__matricula','acidente__condutor__nome','acidente__inspetor__matricula','acidente__inspetor__nome','acidente__endereco','acidente__bairro','acidente__cidade','acidente__uf','acidente__culpabilidade','acidente__concluido','nome','cpf','veiculo','placa','cor','ano','forma','oficina__nome','acordo','id','id')
            
        for acidente in acidentes:
            writer.writerow(acidente)
        consulta = Despesa.objects.values('terceiro').filter(terceiro__acidente__data__range=(periodo_de,periodo_ate)).annotate(valor=Sum('valor')).order_by('terceiro')
        
        # MONTA DICT COM DESPESAS POR TERCEIRO NO PERIODO
        despesas = {}
        for despesa in consulta:
            despesas[despesa['terceiro']] = despesa['valor']
        
        for terceiro in terceiros:
            terceiro = list(terceiro)
            desp = despesas.get(terceiro[0]) or 0
            soma = ((terceiro[27]) or 0) + desp
            terceiro[27] = str(terceiro[27]).replace('.',',')
            terceiro[28] = str(round(desp,2)).replace('.',',')
            terceiro[29] = str(round(soma,2)).replace('.',',')                
            writer.writerow(terceiro)
        return response
    except:
        messages.warning(request,'Erro ao exportar dados. Verifique os filtros')
        return redirect('sinistro_acidentes')