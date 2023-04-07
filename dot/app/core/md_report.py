import re
import csv
from django.http import HttpResponse

# IMPORTS PARA REPORTLAB
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Frame, PageTemplate
# from reportlab.pdfbase.pdfmetrics import stringWidth
# from reportlab.lib.styles import ParagraphStyle
# import locale
# locale.setlocale(locale.LC_ALL, '')

# MD_REPORT
# --
# @version  1.0
# @since    07/04/2023
# @author   Rafael Gustavo Alves {@email castelhano.rafael@gmail.com }
# @desc     Gera PDF baseado em string com markdown (customizado), podendo receber dados dinamicos
# @param    {String} Modelo com o markdown
# @param    {Object} Dicionario com o(s) modelo(s) utilizados
# @returns  {HttpResponse} Retorna PDF
def md_report(original, **kwargs):
    metrics = {
        "ms": 10,       # Margin start
        "me": 10,       # Margin end
        "mt": 30,       # Margin top
        "mb": 20,       # Margin bottom
        "fs": 14,       # Custom font size
        "fc": [0,0,0],    # Custom font color RGB
        "fsh1": 22,     # Foont size H1
        "fsh2": 18,     # Foont size H2
        "fsh3": 16,     # Foont size H3
    }

    LEFT = 0
    CENTER = 1
    RIGHT = 2
    JUSTIFY = 4

    buffer = BytesIO()
    PAGE_WIDTH  = A4[0]
    PAGE_HEIGHT = A4[1]
    doc = SimpleDocTemplate(buffer,topMargin=metrics['mt'],bottomMargin=metrics['mb'],leftMargin=metrics['ms'],rightMargin=metrics['me'])


    # result = re.sub(r"^### (.*$)", r'<h5>\1</h5>', original) # H3
    # result = re.sub(r"^###__ (.*$)", r'<h5>\1</h5>', original) # H3
    # result = re.sub(r"\*\*(.*?)\*\*", r'<b>\1</b>', original) # Bold
    # result = re.sub(r"\*\*(.*?)\*\*", r'<b>\1</b>', original) # Bold
    result = ''
    return result
