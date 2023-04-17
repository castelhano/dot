from reportlab.lib.styles import ParagraphStyle

LEFT = 0
CENTER = 1
RIGHT = 2
JUSTIFY = 4

style_base = ParagraphStyle(
    name='Normal',
    fontName='Helvetica',
    fontSize=12,
    leading=16,
    alignment=JUSTIFY,
    spaceAfter=14
)

style_monospace = ParagraphStyle(
    name='Normal',
    fontName='Courier',
    fontSize=12,
    leading=16,
    alignment=JUSTIFY,
    spaceAfter=5
)

style_base_center = ParagraphStyle(
    name='Normal',
    fontName='Helvetica',
    fontSize=12,
    leading=16,
    alignment=CENTER,
    spaceAfter=14
)

style_base_end = ParagraphStyle(
    name='Normal',
    fontName='Helvetica',
    fontSize=12,
    leading=16,
    alignment=RIGHT,
    spaceAfter=14
)

style_list = ParagraphStyle(
    name='Normal',
    fontName='Helvetica',
    fontSize=12,
    leading=16,
    alignment=JUSTIFY,
    leftIndent=5,
    bulletIndent=7,
    spaceAfter=0
)

style_h1 = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=18,
    alignment=LEFT,
    spaceAfter=20
)

style_h1_center = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=18,
    alignment=CENTER,
    spaceAfter=20
)

style_h1_end = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=18,
    alignment=RIGHT,
    spaceAfter=20
)

style_h2 = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=14,
    leading=16,
    alignment=LEFT,
    spaceAfter=18
)

style_h2_center = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=14,
    leading=16,
    alignment=CENTER,
    spaceAfter=18
)

style_h2_end = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=14,
    leading=16,
    alignment=RIGHT,
    spaceAfter=18
)

style_h3 = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=12,
    leading=16,
    alignment=LEFT,
    spaceAfter=16
)

style_h3_center = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=12,
    leading=16,
    alignment=CENTER,
    spaceAfter=16
)

style_h3_end = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=12,
    leading=16,
    alignment=RIGHT,
    spaceAfter=16
)

style_callout = ParagraphStyle(
    name='Normal',
    fontName='Helvetica',
    fontSize=12,
    leading=16,
    alignment=LEFT,
    textColor='darkslategray',
    spaceAfter=22
)

style_box = ParagraphStyle(
    name='Normal',
    fontName='Helvetica',
    fontSize=12,
    alignment=LEFT,
    spaceBefore=16,
    spaceAfter=16,
    borderWidth=1,
    leftIndent=10,
    borderRadius=3,
    backColor='gainsboro',
    leading=16,
    borderPadding=[5,5,3,10],
    borderColor='gainsboro'
)

signature_styles = [
    ('LINEABOVE', (0,0), (-1,0), 1.5, 'black'),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('LINEBEFORE', (1,0), (-1,0), 12, 'white'),
    ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]