from django.shortcuts import render
from .models import Alerta
from datetime import datetime


def dot_cleaner(request):
    header = {
        'script' : 'dot_cleaner',
        'inicio' : datetime.now(),
    }
    response = []
    response.append(clean_alertas())
    header['termino'] = datetime.now()
    return render(request, 'core/cron.html',{'response':response,'header':header})


def clean_alertas(force=False):
    try:
        if force == True:
            qtde = Alerta.objects.filter(lido=True).delete()
        else:        
            qtde = Alerta.objects.filter(lido=True, critico=False).delete()
        return [True, 'clean_alertas',f'force:<b class="text-primary"> {force}</b>','<b class="text-success">Success</b>', f'Total de <b>{qtde[0]}</b> alertas removidos.']
    except:
        return [False, 'clean_alertas',f'force:<b class="text-primary"> {force}</b>','<b class="text-danger">Error</b>', f'Erro ao apagar alertas']