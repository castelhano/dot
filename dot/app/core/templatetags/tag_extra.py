from datetime import date
import datetime
from django import template


register = template.Library()

@register.filter
def add_days(value, days):
    return value + datetime.timedelta(days=days)

@register.filter
def now_until_date(value):
    return (value - date.today()).days

@register.filter
def sub(minuendo, subtraendo):
    return minuendo - subtraendo

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