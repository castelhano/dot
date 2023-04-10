import re

# IMPORTS PARA REPORTLAB
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.platypus.flowables import PageBreak, HRFlowable
from reportlab.lib.styles import ParagraphStyle

from .md_report_styles import *

# MD_REPORT
# --
# @version  1.0
# @since    07/04/2023
# @author   Rafael Gustavo Alves {@email castelhano.rafael@gmail.com }
# @desc     Gera PDF baseado em string com markdown (customizado), podendo receber dados dinamicos
# @param    {String} Modelo com o markdown
# @param    {Object} Dicionario com o(s) modelo(s) utilizados
# @returns  {PDF_VALUE} Retorna PDF

def md_report(request, original, **kwargs):
    # PARAMETROS    
    PAGE_WIDTH  = A4[0]
    PAGE_HEIGHT = A4[1]
    
    MARGIN_TOP = 50
    MARGIN_BOTTOM = 30
    MARGIN_START = 50
    MARGIN_END = 50
    
    FOOTER_HEIGHT = 0
    FOOTER_SPACE = 12
    
    buffer = BytesIO()

    # Carregando Estilos
    

    # Ajustando o template (somente footer)
    footer_text = ''
    re_footer = re.search(f'\[footer\](.*?)\[\/footer\]', original)
    
    if re_footer:
        style_footer = ParagraphStyle(
            name='Normal',
            fontName='Helvetica',
            fontSize=9,
            alignment=CENTER
        )
        footer_text = re_footer.group(1)
        original = re.sub(f'\[footer\](.*?)\[\/footer\]', '', original) # Retira o footer da string original
        doc = SimpleDocTemplate(buffer,topMargin=MARGIN_TOP,bottomMargin=MARGIN_BOTTOM + len(footer_text.split('<br />')) * 20,leftMargin=MARGIN_START, rightMargin=MARGIN_END)
        FOOTER = Paragraph(footer_text, style_footer)
        w, FOOTER_HEIGHT = FOOTER.wrap(doc.width, doc.bottomMargin)
        
        def footer(canvas, doc):
            canvas.saveState()
            FOOTER.drawOn(canvas, doc.leftMargin, FOOTER_HEIGHT)
            canvas.restoreState()
    else:
        doc = SimpleDocTemplate(buffer,topMargin=MARGIN_TOP,bottomMargin=MARGIN_BOTTOM,leftMargin=MARGIN_START, rightMargin=MARGIN_END)
    
    
    original = re.sub(r"\*\*(.*?)\*\*", r'<b>\1</b>', original) # Bold
    original = re.sub(r"\*(.*?)\*", r'<i>\1</i>', original)     # Italico
    original = re.sub(r"_-(.*?)-_", r'<u>\1</u>', original)     # Tachado
    
    # Preenchendo o doc
    linhas = original.split('\n')
    flowables = []


    for linha in linhas:
        if re.search(r"^### (.*$)", linha):
            flowables.append(Paragraph(re.search(r"^### (.*$)", linha).group(1), style_h3))
        elif re.search(r"^###_ (.*$)", linha):
            flowables.append(Paragraph(re.search(r"^###_ (.*$)", linha).group(1), style_h3_center))
        elif re.search(r"^###__ (.*$)", linha):
            flowables.append(Paragraph(re.search(r"^###__ (.*$)", linha).group(1), style_h3_end))
        elif re.search(r"^## (.*$)", linha):
            flowables.append(Paragraph(re.search(r"^## (.*$)", linha).group(1), style_h2))
        elif re.search(r"^##_ (.*$)", linha):
            flowables.append(Paragraph(re.search(r"^##_ (.*$)", linha).group(1), style_h2_center))
        elif re.search(r"^##__ (.*$)", linha):
            flowables.append(Paragraph(re.search(r"^##__ (.*$)", linha).group(1), style_h2_end))
        elif re.search(r"^# (.*$)", linha):
            flowables.append(Paragraph(re.search(r"^# (.*$)", linha).group(1), style_h1))
        elif re.search(r"^#_ (.*$)", linha):
            flowables.append(Paragraph(re.search(r"^#_ (.*$)", linha).group(1), style_h1_center))
        elif re.search(r"^#__ (.*$)", linha):
            flowables.append(Paragraph(re.search(r"^#__ (.*$)", linha).group(1), style_h1_end))
        elif re.search(r"^___(.*$)", linha):
            flowables.append(Paragraph(re.search(r"^___(.*$)", linha).group(1), style_base_end))
        elif re.search(r"^__(.*$)", linha):
            flowables.append(Paragraph(re.search(r"^__(.*$)", linha).group(1), style_base_center))
        elif re.search(r"^--[-]*?", linha):
            flowables.append(HRFlowable(color='black', spaceBefore=20, spaceAfter=15))
        elif re.search(r"^\> (.*$)", linha):
            flowables.append(Paragraph(re.search(r"^\> (.*$)", linha).group(1), style_callout))
        elif re.search(r"\[\[(.*?)\]\]", linha):
            flowables.append(Paragraph(re.search(r"\[\[(.*?)\]\]", linha).group(1), style_box))
        elif re.search(r"\[\[(.*?)\]\]", linha):
            flowables.append(Paragraph(re.search(r"\[\[(.*?)\]\]", linha).group(1), style_box))
        elif re.search(r"\[break\]", linha):
            flowables.append(PageBreak())
        else:
            flowables.append(Paragraph(linha, style_base))

    if re_footer:
        doc.build(flowables, onFirstPage=footer, onLaterPages=footer)
    else:
        doc.build(flowables)

    pdf_value = buffer.getvalue()
    buffer.close()
    
    return pdf_value
    
    # result = re.sub(r"^### (.*$)", r'<h5>\1</h5>', original) # H3
    # result = re.sub(r"^###__ (.*$)", r'<h5>\1</h5>', original) # H3
    # result = re.sub(r"\*\*(.*?)\*\*", r'<b>\1</b>', original) # Bold
    # result = re.sub(r"\*\*(.*?)\*\*", r'<b>\1</b>', original) # Bold
    # result = ''