from django.shortcuts import render
from .models import Alerta, Log
from globus.models import Escala
from datetime import datetime, date, timedelta

# Funcao principal do modulo cron, recebe parametros via get e/ou **kargs e chama as rotinas correspondente
# --
# @version  1.0
# @since    08/03/2022
# @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
# @param    {Dics} **kargs Dicionario com parametros
# @param    {Dics} request.GET.dict() Recebe parametros informados na url
# @returns  {Array} Retorna lista com resultado e parametros de cada subrotina
# @example  dot_cleaner(request, **kargs)
# @example  http://...../cron/dot_cleaner?cleanlogs=True&cleanalertas=True&force=True&until=2022-05-01
def dot_cleaner(request, **kargs):
    header = {
        'script' : 'dot_cleaner',
        'inicio' : datetime.now(),
    }
    response = []
    if request.method == 'GET':
        get_parameters = request.GET.dict() # Pega os parametros enviados via get
        kargs = {**kargs, **get_parameters} # Merge nos dois dicts !! No python 3.9 pode ser alterado para kargs = kargs | get_parameters
    
    if 'cleanalertas' in kargs and kargs['cleanalertas'] == 'True':
        response.append(clean_alertas(**kargs))
    if 'cleanlogs' in kargs and kargs['cleanlogs'] == 'True':
        response.append(clean_logs(**kargs))
    if 'cleanescalas' in kargs and kargs['cleanescalas'] == 'True':
        response.append(clean_escalas(**kargs))
    header['termino'] = datetime.now()
    if request.method == 'GET':
        return render(request, 'core/cron.html',{'response':response,'header':header})
    else: # Retorno para chamada via console
        return {'response':response,'header':header}
        


def clean_alertas(**kargs):
    force = True if 'force' in kargs and kargs['force'] == 'True' else False
    try:
        if force:
            qtde = Alerta.objects.filter(lido=True).delete()
        else:        
            qtde = Alerta.objects.filter(lido=True, critico=False).delete()
        return [True, 'clean_alertas',f'force:<b class="text-primary"> {force}</b>','<b class="text-success">Success</b>', f'Total de <b>{qtde[0]}</b> alertas removidos.']
    except Exception as e:
        return [False, 'clean_alertas',f'force:<b class="text-primary"> {force}</b>', list(e)[0]]

def clean_logs(**kargs):
    until = kargs['until'] if 'until' in kargs else date.today() - timedelta(days=365)
    try:
        qtde = Log.objects.filter(data__lte=until).delete()
        return [True, 'clean_logs',f'until:<b class="text-primary"> {until}</b>','<b class="text-success">Success</b>', f'Total de <b>{qtde[0]}</b> logs removidos.']
    except Exception as e:
        return [False, 'clean_logs',f'until:<b class="text-primary"> {until}</b>','<b class="text-danger">Error</b>', list(e)[0]]

def clean_escalas(**kargs):
    until = kargs['until'] if 'until' in kargs else date.today() - timedelta(days=30)
    try:
        qtde = Escala.objects.filter(data__lte=until).delete()
        return [True, 'clean_escalas',f'until:<b class="text-primary"> {until}</b>','<b class="text-success">Success</b>', f'Total de <b>{qtde[0]}</b> escalas removidas.']
    except Exception as e:
        return [False, 'clean_escalas',f'until:<b class="text-primary"> {until}</b>','<b class="text-danger">Error</b>', list(e)[0]]