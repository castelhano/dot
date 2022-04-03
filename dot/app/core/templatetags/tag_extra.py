from datetime import date
from django import template
from urllib.parse import urlparse, parse_qs
import datetime


register = template.Library()

@register.filter
def add_days(value, days):
    return value + datetime.timedelta(days=days)

@register.filter
def remove_char(value, char):
    return value.replace(char,'')

@register.filter
def now_until_date(value):
    return (value - date.today()).days if value else '--'

@register.filter
def sub(minuendo, subtraendo):
    return minuendo - subtraendo

@register.filter
def percentual(valor, total):
    return (valor / total) * 100 if total > 0 else '---'

@register.filter
def zfill(valor,casas):
    return str(valor).zfill(int(casas))

@register.filter
def get_field(objeto,field):
    # NAO ACEITA METODOS
    return getattr(objeto, field)

@register.filter
def dict_value(dict,key):
    return dict.get(key)

# filter indicatorArrow
# @desc     Retorna icone de arrow correspondente ao valor (use filter |safe para exibir html correspondente)
# @param    {Number} value Valor alvo
# @param    {Bool} maior_melhor (opcional) Se definido como False inverte a ordem das arrows
# @returns  {html} Tag html correspondente ao valor
# @example  obj.value|indicatorArrow|safe ou obj.value|indicatorArrow:True|safe
@register.filter
def indicatorArrow(value, maior_melhor=True):
    if value < 0:
        return f'<i class="fas fa-arrow-down text-danger"></i>' if maior_melhor else f'<i class="fas fa-arrow-down text-success"></i>'
    elif value > 0:
        return f'<i class="fas fa-arrow-up text-success"></i>' if maior_melhor else f'<i class="fas fa-arrow-up text-danger"></i>'
    else:
        return f'<i class="fas fa-minus text-secondary"></i>'

# filter stars
# @desc     Retorna icone de stars correspondente a quantidade informada (use filter |safe para exibir html correspondente)
# @param    {Int} value Avaliacao
# @returns  {html} Tag html correspondente ao valor
# @example  obj.value|stars|safe ou obj.value|indicatorArrow:True|safe
@register.filter
def stars(value):
    s = ''
    for x in range(5):
        s += '<i class="fas fa-star"></i>' if value >= x + 1 else '<i class="far fa-star"></i>'
    return s

@register.filter
def url_get(request,parameter):
    parsed_url = urlparse(request.get_full_path())
    try:
        return parse_qs(parsed_url.query)[parameter][0]
    except KeyError as e:
        return None
