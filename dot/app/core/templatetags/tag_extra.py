from datetime import date
from django import template
from urllib.parse import urlparse, parse_qs
import datetime


register = template.Library()

# call_method Metodo chama funcao de objeto passando parametros
# --
# @version  1.0
# @since    09/04/2022
# @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
# @example  {% call_method indicador 'analises_pendentes' metrics.empresa.id as analises_pendentes %}
#           <p>{{analises_pendentes}}</p> ou for i in analises_pendentes ......
@register.simple_tag
def call_method(obj, method_name, *args):
    try:
        method = getattr(obj, method_name)
        return method(*args)
    except Exception as e:
        return 'err'

# add_days Recebe uma data e adiciona x dias
# --
# @version  1.0
# @since    10/11/2021
# @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
# @example  {{data|add_days:5}} ou {{data|add_days:-5}}
@register.filter
def add_days(value, days):
    return value + datetime.timedelta(days=days)

# now_until_date Calcula a diferenca em dias de hoje ate uma data informada
# --
# @version  1.0
# @since    10/11/2021
# @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
# @example  {{data|now_until_date}} dias
@register.filter
def now_until_date(value):
    return (value - date.today()).days if value else '--'

# days_since Retorna a quantidade de dias entre duas datas
# --
# @version  1.0
# @since    10/04/2022
# @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
# @example  {{data|now_until_date}} dias
@register.filter
def days_since(v1, v2):
    return (v2 - v1).days if v1 and v2 else None

# sub Subtrai dois valores
# --
# @version  1.0
# @since    10/11/2021
# @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
# @example  {{valor|sub:outro_valor}}
@register.filter
def sub(minuendo, subtraendo):
    return minuendo - subtraendo

# percentual Retorna o valor percentual de determinado valor
# --
# @version  1.0
# @since    05/10/2021
# @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
# @example  {{valor|percentual:total}}
@register.filter
def percentual(valor, total):
    return (valor / total) * 100 if total > 0 else '---'

# zfill Retorna valor completando com zeros n vezes
# --
# @version  1.0
# @since    05/10/2021
# @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
# @example  {{2|zfill:5}} -> 00002
@register.filter
def zfill(valor,casas):
    return str(valor).zfill(int(casas))

# dict_value Retorna valor de dicionario informando a key
# --
# @version  1.0
# @since    05/10/2021
# @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
# @example  {{metrics.marcas_sum|dict_value:key|zfill:2}}
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
    try:
        if int(value) < 0:
            return f'<i class="fas fa-arrow-down text-danger"></i>' if maior_melhor else f'<i class="fas fa-arrow-down text-success"></i>'
        elif int(value) > 0:
            return f'<i class="fas fa-arrow-up text-success"></i>' if maior_melhor else f'<i class="fas fa-arrow-up text-danger"></i>'
        else:
            return f'<i class="fas fa-minus text-muted"></i>'
    except Exception as e:
        return ''

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

# url_get Retorna valor (ou None) de variavel informada na url
# @version  1.0
# @since    05/10/2021
# @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
# @example  {% if request|url_get:'from' == 'consultar_escala' %}
@register.filter
def url_get(request,parameter):
    parsed_url = urlparse(request.get_full_path())
    try:
        return parse_qs(parsed_url.query)[parameter][0]
    except KeyError as e:
        return None