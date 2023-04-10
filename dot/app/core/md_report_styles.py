from reportlab.lib.styles import ParagraphStyle

LEFT = 0
CENTER = 1
RIGHT = 2
JUSTIFY = 4

style_base = ParagraphStyle(
    name='Normal',
    fontName='Helvetica',
    fontSize=12,
    alignment=JUSTIFY,
    spaceAfter=14
)

style_base_center = ParagraphStyle(
    name='Normal',
    fontName='Helvetica',
    fontSize=12,
    alignment=CENTER,
    spaceAfter=14
)

style_base_end = ParagraphStyle(
    name='Normal',
    fontName='Helvetica',
    fontSize=12,
    alignment=RIGHT,
    spaceAfter=14
)

style_h1 = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=16,
    alignment=LEFT,
    spaceAfter=20
)

style_h1_center = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=16,
    alignment=CENTER,
    spaceAfter=20
)

style_h1_end = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=16,
    alignment=RIGHT,
    spaceAfter=20
)

style_h2 = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=14,
    alignment=LEFT,
    spaceAfter=18
)

style_h2_center = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=14,
    alignment=CENTER,
    spaceAfter=18
)

style_h2_end = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=14,
    alignment=RIGHT,
    spaceAfter=18
)

style_h3 = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=12,
    alignment=LEFT,
    spaceAfter=16
)

style_h3_center = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=12,
    alignment=CENTER,
    spaceAfter=16
)

style_h3_end = ParagraphStyle(
    name='Normal',
    fontName='Helvetica-Bold',
    fontSize=12,
    alignment=RIGHT,
    spaceAfter=16
)

style_callout = ParagraphStyle(
    name='Normal',
    fontName='Helvetica',
    fontSize=14,
    alignment=LEFT,
    spaceAfter=18
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
    backColor='darkgray',
    # backColor='whitesmoke',
    leading=16,
    borderPadding=[8,5,8,10],
    borderColor='darkgray'
)