from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from .models import Ocorrencia, Notificacao
from core.models import Empresa
from datetime import date, datetime
from django.db.models import Count
# IMPORTS PARA REPORTLAB
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Frame, PageTemplate
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.styles import ParagraphStyle
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

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
    ocorrencias_inspetor = ocorrencias.values('usuario__username').annotate(qtd=Count('usuario')).exclude(usuario=None).order_by('-qtd')
    
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
        evolucao_ocorrencias_metrics['bgcolors'].append(bg.purple)
        evolucao_ocorrencias_metrics['bordercolors'].append(bc.purple)
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
        ocorrencias_linha_metrics['bgcolors'].append(bg.purple)
        ocorrencias_linha_metrics['bordercolors'].append(bc.purple)
    
    
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
        'ocorrencias_inspetor': ocorrencias_inspetor,
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

#  ------------------------------------

@login_required
@permission_required('trafego.view_notificacao')
def notificacao_capa(request):
    notificacao = Notificacao.objects.get(pk=request.GET['notificacao'])
    
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
        spaceAfter=255
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
        
        
        # DADOS RESUMO NOTIFICACAO
        info_start = 145
        info_line_gap = 20
        info_current_h = 720
        
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(doc.width - 80,720, 'No.')
        canvas.setFont("Helvetica-Bold", 20)
        pasta_size = stringWidth(notificacao.codigo,"Helvetica-Bold", 16)
        canvas.drawString(doc.width - 50,718, notificacao.codigo)
        
        indice_size = stringWidth('Empresa:',"Helvetica", 12)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 12)
        canvas.drawString(indice_start, info_current_h ,'Empresa:')
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(info_start, info_current_h, notificacao.empresa.nome if notificacao.empresa else '--')
        
        indice_size = stringWidth('Data:',"Helvetica", 12)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 12)
        info_current_h -= info_line_gap
        canvas.drawString(indice_start, info_current_h ,'Data:')
        canvas.setFont("Helvetica-Bold", 12)
        msg_data = notificacao.data.strftime("%d/%m/%Y")
        msg_data += "  " + notificacao.hora.strftime("%H:%M") if notificacao.hora != None else ''
        canvas.drawString(info_start, info_current_h, msg_data)
        
        indice_size = stringWidth('Carro:',"Helvetica", 12)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 12)
        info_current_h -= info_line_gap
        canvas.drawString(indice_start,info_current_h,'Carro:')
        canvas.setFont("Helvetica-Bold", 12)
        veiculo_text = f'{notificacao.veiculo.prefixo}   {notificacao.veiculo.placa}' if notificacao.veiculo else '--'
        veiculo_text += '   [ LACRADO ]' if notificacao.veiculo_lacrado else ''
        canvas.drawString(info_start,info_current_h, veiculo_text)
        
        indice_size = stringWidth('Linha:',"Helvetica", 12)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 12)
        info_current_h -= info_line_gap
        canvas.drawString(indice_start,info_current_h,'Linha:')
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(info_start,info_current_h, f'{notificacao.linha.codigo} - {notificacao.linha.nome}' if notificacao.linha else '--')
        
        indice_size = stringWidth('Condutor:',"Helvetica", 12)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 12)
        info_current_h -= info_line_gap
        canvas.drawString(indice_start,info_current_h,'Condutor:')
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(info_start,info_current_h, f'{notificacao.funcionario.matricula} {notificacao.funcionario.nome}' if notificacao.funcionario else '--')
        
        indice_size = stringWidth('Local:',"Helvetica", 12)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 12)
        info_current_h -= info_line_gap
        canvas.drawString(indice_start,info_current_h,'Local:')
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(info_start,info_current_h, notificacao.local.nome if notificacao.local else '--')
        
        indice_size = stringWidth('Enquadram:',"Helvetica", 12)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 12)
        info_current_h -= info_line_gap
        canvas.drawString(indice_start,info_current_h,'Enquadram:')
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(info_start,info_current_h, f'{notificacao.enquadramento.codigo} - {notificacao.enquadramento.nome}' if notificacao.enquadramento else '--')
        
        indice_size = stringWidth('Valor:',"Helvetica", 12)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 12)
        info_current_h -= info_line_gap
        canvas.drawString(indice_start,info_current_h,'Valor:')
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(info_start,info_current_h, f'R$ {locale.currency(notificacao.valor, grouping=True, symbol=None)}')
        
        indice_size = stringWidth('Orgão:',"Helvetica", 12)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 12)
        info_current_h -= info_line_gap
        canvas.drawString(indice_start,info_current_h,'Orgão:')
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(info_start,info_current_h, notificacao.agente.orgao.nome if notificacao.agente else '--')
        
        indice_size = stringWidth('Agente:',"Helvetica", 12)
        indice_start = 140 - indice_size
        canvas.setFont("Helvetica", 12)
        info_current_h -= info_line_gap
        canvas.drawString(indice_start,info_current_h,'Agente:')
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(info_start,info_current_h, f'{notificacao.agente.matricula} {notificacao.agente.nome}' if notificacao.agente else '--')
        
        # DETALHAMENTO ACIDENTE
        canvas.setDash(1,2)
        canvas.setLineWidth(0)
        canvas.line(MX + 30,530, PAGE_WIDTH - 60,530)
        
        # Adiciona Detalhes da Notificacao
        P = Paragraph(notificacao.detalhe.replace('\n','<br />') + '<br />---<br />', paragrafo_style)
        flowables.append(P)
        P = Paragraph(notificacao.tratativa.replace('\n','<br />'), paragrafo_style)
        flowables.append(P)
        
        # canvas.line(MX + 30,200, PAGE_WIDTH - 60,200)

        # ESCREVENDO ASSINATURAS
        canvas.setDash(1)
        canvas.setLineWidth(1)
        canvas.line(MX,135,(PAGE_WIDTH / 2)- 10,135)
        canvas.line(PAGE_WIDTH-(PAGE_WIDTH / 2 - 10),135,PAGE_WIDTH - MX,135)
        canvas.setFont("Helvetica-Bold", 9)
        
        sinistro_size = stringWidth('GERENCIA OPERACAO',"Helvetica-Bold", 9)
        gerencia_size = stringWidth('JURIDICO',"Helvetica-Bold", 9)
        
        sinistro_start = ((PAGE_WIDTH / 2) - sinistro_size) / 2 + 10
        gerencia_start = (PAGE_WIDTH / 2) + (((PAGE_WIDTH / 2 - gerencia_size) / 2) - 10)
        
        canvas.drawString(sinistro_start,120,'GERENCIA OPERACAO')
        canvas.drawString(gerencia_start,120,'JURIDICO')
        
        # ESCREVENDO RODAPE
        rodape_empresa = notificacao.empresa.razao_social
        rodape_l1 = notificacao.empresa.endereco + ' Bairro ' + notificacao.empresa.bairro + ' ' + notificacao.empresa.cidade + '-' + notificacao.empresa.uf
        rodape_l2 = 'CEP ' + notificacao.empresa.cep + ' | ' + 'CNPJ: ' + notificacao.empresa.cnpj
        
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
    titulo = '\nREGISTRO DE AUTO DE INFRAÇÃO OPERACIONAL'
    flowables.append(Paragraph(titulo,titulo_style))

    
    doc.build(flowables)
    pdf_value = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="capa.pdf"'
    
    response.write(pdf_value)
    return response
