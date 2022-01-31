import re
from .models import Alerta, Log
from pessoal.models import Funcionario
from django.contrib.auth.models import User

def Run(request, script):
    rows = script.split('\n')
    response = []
    for row in rows:
        try:
            command = re.search(r'@(.*?) ', row).group(1)
            attrs = re.search('{(.*)}', row).group(1)
            if command == 'runscript':
                response.append(runScript(request, attrs))
            elif command == 'alert':
                if '#clean' in attrs:
                    response.append(alertaClean(request, attrs))
                else:
                    response.append(alertaAdd(request, attrs))
            elif command == 'logs':
                response.append(logs(request, attrs))
            elif command == 'employee':
                response.append(funcionario(request, attrs))
            else: # Comando nao reconhecido, gera exception de bad formated
                raise Exception()
        except:
            response.append('<span><b class="text-danger">Error:</b> Bad formatted attributes, command aborted</span>')
    return response

def runScript(request, attrs):
    response = '<span><b class="text-orange">Alert:</b> To run the script set <b class="text-orange">execute=True</b></span>'
    if '!execute=True' in attrs:
        code = re.search(':code=([^\s]+)', attrs).group(1)
        response = f'<span><b class="text-orange">Alert:</b> Code <b>{code}</b> not configured</span>'
        if code == '666':
            from pessoal.models import Funcionario
            func = Funcionario.objects.get(matricula='10120')
            func.status = 'A'
            func.save()
            response = f'<span><b class="text-success">Done:</b></span>'
    return response

def alertaClean(request, attrs):
    try:
        until = re.search(':until=([^\s]+)', attrs).group(1)
        qtde = Alerta.objects.filter(lido=True,create_at__lte=until).delete()[0]
        response = f'<span><b class="text-success">Done:</b> Total of {qtde} alerts deleted</span>'
    except:
        response = '<span><b class="text-danger">Error:</b> Bad formatted attributes, command aborted</span>'
    return response

def alertaAdd(request, attrs):
    response = '<span><b class="text-danger">Error:</b> Bad formatted attributes, alert not created</span>'
    fields = {}
    errors = False
    try:
        fields['mensagem'] = re.search('msg:(.*)+;', attrs).group(0).replace('msg:','')[:-1] # Separa a mensagem do script e adiciona no dicionario
    except:
        errors = True
    if errors:
        return response
    attrs_list = re.sub('msg:(.*)+;','', attrs).split(' ') # Remove a mensagem do script e cria lista com atributos restantes
    for attr in attrs_list:
        if len(attr) == 0: # Ignora espaços em branco entre os atributos
            pass
        elif attr[0] == '#' and not errors: # Atribui usuário ou all 
            username = attr[1:]
            if username == 'all':
                fields['usuario'] = 'all'
            else:
                try:
                    fields['usuario'] = User.objects.get(username=username)
                except:
                    errors = True
                    response = f'<span><b class="text-danger">Error:</b> User <b>{username}</b> nor found, alert not created</span>'
        elif attr[0] == ':' and not errors: # Entrada eh um atributo, adiciona no dicionario para metodo create
            f = attr[1:].split('=')
            fields[f[0]] = f[1].replace(';', ' ').replace('_',' ')
        elif attr[0] == '!' and not errors: # Entrada eh um atributo, adiciona no dicionario para metodo create
            f = attr[1:].split('=')
            fields[f[0]] = f[1]
        elif not errors: # Entrada não se encaixa em nenhuma das predefinidas, descarta entrada
            pass
    if not errors and isinstance(fields['usuario'], User): # Cria o alerta para usuario especifico (caso instanciado) e caso nao tenha erros
        try:
            alerta = Alerta.objects.create(**fields)
            response = f'<b class="text-success">Done:</b> Alert create for user <b class="text-success">{username.title()}</b>'
        except:
            errors = True
    elif not errors and fields['usuario'] == 'all': # Cria o alerta para todos os usuario do sistema
        try:
            usuarios = User.objects.filter(is_active=True)
            for user in usuarios:
                fields['usuario'] = user
                alerta = Alerta.objects.create(**fields)
            response = f'<b class="text-success">Done:</b> Alert create for ALL <b class="text-success">active users'
        except:
            errors = True
            response = f'<span><b class="text-danger">Error:</b> Something went wrong, alert not created</span>'
    else:
        pass
    return response

def logs(request, attrs):
    try:
        until = re.search(':until=([^\s]+)', attrs).group(1)
        if not '#clean' in attrs:
            raise Exception()
        if ':model=' in attrs:
            modelo = re.search(':model=(.*) ', attrs).group(1)
            qtde = Log.objects.filter(data__lte=until, modelo=modelo).delete()[0]
        else:
            qtde = Log.objects.filter(data__lte=until).delete()[0]
        response = f'<b class="text-success">Done:</b> Total of <b>{qtde}</b> logs deleted.'
    except:
        response = '<span><b class="text-danger">Error:</b> Bad formatted attributes, <b class="text-danger">operation aborted</b>.</span>'
    return response

def funcionario(request, attrs):
    response = '<span><b class="text-danger">Error:</b> Bad formatted attributes, <b class="text-danger">operation aborted</b>.</span>'
    try:
        operacao = re.search('!([^\s]+) ', attrs).group(1)
        matricula = re.search('#([^\s]+) ', attrs).group(1)
        if operacao == 'reengage':
            funcionario = Funcionario.objects.get(matricula=matricula)
            funcionario.status = 'A'
            funcionario.data_desligamento = None
            funcionario.motivo_desligamento = ''
            funcionario.save()
            l = Log()
            l.modelo = "pessoal.funcionario"
            l.objeto_id = str(funcionario.id)
            l.objeto_str = str(funcionario.matricula)
            l.usuario = request.user
            l.mensagem = "REENGAGE"
            print('AQUII')
            l.save()
            print('AQUII 22')
            response = f'<b class="text-success">Done:</b> Employee <b>{matricula}</b> reengage'
        else:
            pass
    except:
        pass
    return response