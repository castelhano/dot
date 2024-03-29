import re
from django.conf import settings as ROOT
from datetime import date, datetime, time
from decimal import Decimal
import locale
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# IMPORTS PARA REPORTLAB
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table
from reportlab.platypus.flowables import PageBreak, HRFlowable
from reportlab.lib.styles import ParagraphStyle

# IMPORT DE ESTILOS
from .md_report_styles import *

# MD_REPORT
# --
# @version  1.6
# @since    04/04/2023
# @release  14/04/2023
# @author   Rafael Gustavo Alves {@email castelhano.rafael@gmail.com }
# @desc     Gera PDF baseado em string com markdown (extendido), podendo receber dados dinamicos
# @param    {request}   Requisição
# @param    {String}    String com o markdown
# @param    {**kwargs}  Dicionario com o(s) objetos(s) utilizados
# @returns  {PDF_VALUE} Retorna PDF
def md_report(request, original, **kwargs):
    # PARAMETROS    
    PAGE_WIDTH, PAGE_HEIGHT  = A4
    
    MARGIN_TOP = 50
    MARGIN_BOTTOM = 30
    MARGIN_START = 50
    MARGIN_END = 50
    
    FOOTER_HEIGHT = 0
    FOOTER_SPACE = 12

    # Configurando os commons.fields
    hoje = date.today()
    common = {
        "today": hoje.strftime('%d/%m/%Y'),
        "today_full": hoje.strftime('%d de %B de %Y'),
        "now": datetime.now().strftime('%H:%M:%S')
    }
    
    buffer = BytesIO()

    # Ajustando o template
    # Logo
    footer_text = ''
    re_logo = re.search(r'\!\[(.*?)\]\((.*?)\)', original)
    if re_logo:
        original = re.sub(r'\!\[(.*?)\]\((.*?)\)','', original)
    
    # Footer
    re_footer = re.search(f'\[footer\](.*?)\[\/footer\]', original)
    
    # Signature fields
    re_signature = re.search(f'\[signature\](.*?)\[\/signature\]', original)

    style_footer = ParagraphStyle(
        name='Normal',
        fontName='Helvetica',
        fontSize=9,
        alignment=CENTER
    )
    if re_footer:
        if re_footer.group(1) != '':
            footer_text = md_basic(re_footer.group(1))
            footer_text = data_plot(footer_text, **kwargs)
            footer_text = common_plot(footer_text, common)
        elif kwargs['empresa'].footer != '':
            footer_text = md_basic(kwargs['empresa'].footer.replace('\n', '<br />'))
        else:
            footer_text = ''
    else:
        footer_text = ''
    
    if re_logo:
        props = re_logo.group(1).split(',')
        logo_w = int(props[0])
        logo_h = int(props[1])
        logo_ancor = props[2].split('-')[0]
    else:
        logo_h = 0
        logo_ancor = False
    original = re.sub(f'\[footer\](.*?)\[\/footer\]', '', original) # Retira o footer da string original
    doc = SimpleDocTemplate(buffer,topMargin=MARGIN_TOP + logo_h if logo_ancor == 'TOP' else MARGIN_TOP, bottomMargin=MARGIN_BOTTOM + len(footer_text.split('<br />')) * 20,leftMargin=MARGIN_START, rightMargin=MARGIN_END)
    FOOTER = Paragraph(footer_text, style_footer)
    w, FOOTER_HEIGHT = FOOTER.wrap(doc.width, doc.bottomMargin)

    if re_signature and re_signature.group(1) != '':
        signs = re_signature.group(1).split(';')
        sig_names = []
        sig_roles = []
        for sig in signs:
            sig_targets = sig.replace('{','').replace('}','').split(',')
            if len(sig_targets) == 2:
                sig_names.append(data_plot(sig_targets[0], **kwargs))
                sig_roles.append(data_plot(sig_targets[1], **kwargs))
            elif len(sig_targets) == 1:
                sig_names.append(data_plot(sig_targets[0], **kwargs))
                sig_roles.append('')
        sign_tbl = [sig_names,sig_roles]
        original = re.sub(f'\[signature\](.*?)\[\/signature\]','', original)

    def basic_template(canvas, doc):
        canvas.saveState()
        canvas.setTitle('MD Report')
        if re_logo:
            if len(props) == 2:
                props[2] = 'TOP-LEFT'
            position = {
                'TOP-LEFT': [MARGIN_START, PAGE_HEIGHT - 70],
                'TOP-RIGHT': [PAGE_WIDTH - (MARGIN_END + logo_w), PAGE_HEIGHT - 70],
                'TOP-CENTER': [PAGE_WIDTH / 2 - (logo_w / 2), PAGE_HEIGHT - 70],
                'BOTTOM-LEFT': [MARGIN_START, MARGIN_BOTTOM],
                'BOTTOM-CENTER': [PAGE_WIDTH / 2 - (logo_w / 2), MARGIN_BOTTOM],
                'BOTTOM-RIGHT': [PAGE_WIDTH - (MARGIN_END + logo_w), MARGIN_BOTTOM],
            }
            if re_logo.group(2) == '':
                if kwargs['empresa'].logo != '':
                    canvas.drawInlineImage(ROOT.MEDIA_ROOT + '/' + str(kwargs['empresa'].logo), position[props[2]][0], position[props[2]][1], logo_w, logo_h)
            else:
                canvas.drawInlineImage(re_logo.group(2), position[props[2]][0], position[props[2]][1], logo_w, logo_h)                
        FOOTER.drawOn(canvas, doc.leftMargin, FOOTER_HEIGHT)
        # Inserindo linha separadora do footer
        canvas.setLineWidth(1)
        canvas.line(40, doc.bottomMargin - 10, 550, doc.bottomMargin - 10)
        canvas.restoreState()
    
    original = md_basic(original)    
    original = common_plot(original, common)    
    original = data_plot(original, **kwargs)
    flowables = md_layout(original)
    if re_signature:
        colSize = min((PAGE_WIDTH - (MARGIN_START + MARGIN_END) - (len(sig_names) * 12)) / len(sig_names), 280)
        tbl = Table(sign_tbl, colWidths=colSize)
        tbl.setStyle(signature_styles)
        flowables.append(tbl)

    doc.build(flowables, onFirstPage=basic_template, onLaterPages=basic_template)

    pdf_value = buffer.getvalue()
    buffer.close()
    
    return pdf_value
    

def md_basic(original):
    original = re.sub(r"\*\*\*(.*?)\*\*\*", r'<b><i>\1</i></b>', original) # Bold and Italic
    original = re.sub(r"\*\*(.*?)\*\*", r'<b>\1</b>', original) # Bold
    original = re.sub(r"\*(.*?)\*", r'<i>\1</i>', original)     # Italico
    original = re.sub(r"_-(.*?)-_", r'<u>\1</u>', original)     # Tachado
    original = re.sub(r"==(.*?)==", r'<font color="ReportLabFidBlue">\1</font>', original) # Texto de alerta
    original = re.sub(r"=\-(.*?)\-=", r'<font color="firebrick">\1</font>', original) # Texto de alerta
    original = re.sub(r"=\+(.*?)\+=", r'<font color="darkgreen">\1</font>', original) # Texto de alerta
    original = re.sub(r"\[\.\.\.\]", r'&nbsp;&nbsp;&nbsp;&nbsp;', original) # Texto identado
    return original

def common_plot(original, common):
    attrs = re.findall(r"\&\((.*?)\)", original)
    for attr in attrs:
        try:
            target = attr.split('.', 1)
            result = common[target[1]]
            original = original.replace(f'&({attr})', f'{result}')
        except:
            original = original.replace(f'&({attr})', '')
    return original

def data_plot(original, **kwargs):
    attrs = re.findall(r"\$\((.*?)\)", original)
    for attr in attrs:
        target = attr.split('.', 1)
        try:
            result = get_repr(get_field(kwargs[target[0]], target[1]))
            original = original.replace(f'$({attr})', f'{result}')
        except:
            original = original.replace(f'$({attr})', '')
    return original

def md_layout(original):
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
        elif re.search(r"^\&-(.*$)", linha):
            flowables.append(Paragraph(re.sub(r"^&-(.*$)",r"<bullet>&bull;</bullet> \1", linha), style_list))
        elif re.search(r"^___(.*$)", linha):
            flowables.append(Paragraph(re.search(r"^___(.*$)", linha).group(1), style_base_end))
        elif re.search(r"^__(.*$)", linha):
            flowables.append(Paragraph(re.search(r"^__(.*$)", linha).group(1), style_base_center))
        elif re.search(r"^--[-]*?", linha):
            flowables.append(HRFlowable(color='black', spaceBefore=20, spaceAfter=15))
        elif re.search(r"^\>- (.*$)", linha):
            flowables.append(Paragraph(re.search(r"^\>- (.*$)", linha).group(1), style_monospace))
        elif re.search(r"^\> (.*$)", linha):
            flowables.append(Paragraph('<font face="Helvetica-Bold" color="grey" size="16">|</font>&nbsp;&nbsp;' + re.search(r"^\> (.*$)", linha).group(1), style_callout))
        elif re.search(r"\[\[(.*?)\]\]", linha):
            flowables.append(Paragraph(re.search(r"\[\[(.*?)\]\]", linha).group(1), style_box))
        # elif re.search(r"\^[\.\.\.\]", linha):
        #     flowables.append(Paragraph(re.sub(r"\[\.\.\.\]",'&nbsp;&nbsp;&nbsp;&nbsp;', linha), style_base))
        elif re.search(r"\[break\]", linha):
            flowables.append(PageBreak())
        else:
            flowables.append(Paragraph(linha, style_base))

    return flowables

def get_repr(value): 
    if callable(value):
        return '%s' % value()
    return value

def get_field(instance, field):
    field_path = field.split('.')
    attr = instance
    for elem in field_path:
        try:
            attr = getattr(attr, elem)
            if isinstance(attr, date):
                attr = attr.strftime('%d/%m/%Y')
            elif isinstance(attr, time):
                attr = attr.strftime('%H:%M')
            elif isinstance(attr, Decimal):
                attr = locale.currency(attr, grouping=True)
        except AttributeError:
            return ''
    return attr