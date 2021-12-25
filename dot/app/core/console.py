import re
from .models import Alerta
from django.contrib.auth.models import User

def Run(script):
    rows = script.split('\n')
    response = []
    for row in rows:
        command = re.search(r'@(.*?) ', row).group(1)
        attrs = re.search('{(.*)}', row).group(1).split(' ')
        if command == 'alert':            
            response.append(alertaAdd(attrs))
    return response

def alertaAdd(attrs):
    response = ''
    fields = {}
    errors = False
    for attr in attrs:
        if len(attr) == 0: # Ignora espaços em branco entre os atributos
            pass
        elif attr[0] == '#' and not errors: # Atribui usuário ou all 
            username = attr[1:]
            if username == 'all':
                fields['usuario'] = 'all'
            else:
                # try:
                    fields['usuario'] = User.objects.get(username=username)
                # except:
                #     errors = True
                #     response = f'<span><b class="text-danger">Error:</b> User <b>{username}</b> nor found, alert not created</span><br />'
        elif attr[0] == ':' and not errors: # Entrada eh um atributo, adiciona no dicionario para metodo create
            f = attr[1:].split('=')
            fields[f[0]] = f[1].replace(';', ' ')
        elif attr[:4] == 'msg:' and not errors: # Mensagem do alert eh inserido como atricuto no dicionario
            # fields['mensagem'] = re.search('__(.*)__', attr).group(1)
            print('ENTREI')
            print('>> ', re.search('\[(.*?)\]', attr).group(1))
        elif not errors: # Entrada não se encaixa em nenhuma das predefinidas, descarta entrada
            pass
    if not errors and isinstance(fields['usuario'], User): # Cria o alerta para usuario especifico (caso instanciado) e caso nao tenha erros
        try:
            # alerta = Alerta.objects.create(**fields)
            # response = f'<b class="text-success">Done:</b> Alert create for user <b class="text-success">{fields['usuario'].username}</b>'
            response = fields
        except:
            errors = True
            response = f'<span><b class="text-danger">Error:</b> Bad formatted attributes, alert not created -> {fields}</span><br />'
    return response