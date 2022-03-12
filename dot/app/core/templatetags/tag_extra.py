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
    return (value - date.today()).days

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

@register.filter
def url_get(request,parameter):
    parsed_url = urlparse(request.get_full_path())
    try:
        return parse_qs(parsed_url.query)[parameter][0]
    except KeyError as e:
        return None
