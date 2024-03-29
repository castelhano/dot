from .models import Alerta, Log
from .cron import dot_cleaner
from pessoal.models import Funcionario
from .models import Profile
from globus.models import Escala
from django.contrib.auth.models import User

def Run(request, script):
    message = ''
    for k, v in script.items():
        if k == '@alert':
            message = alerta(v)
        elif k == '@runscript':
            message = runScript(request, v)
        elif k == '@pessoal':
            message = pessoal(request, v)
        elif k == '@user':
            message = usuario(request, v)
        elif k == '@globus':
            message = globus(request, v)
        elif k == '@dotCleaner':
            data = dot_cleaner(request, **v) # Funcao retorna dicionario com resultado das subrotinas
            return {'path':'core/cron.html', 'data':data}
        else:
            message = [False, '<b>Rotina inválida</b>, verifique os dados digitados']
    return message
    
def alerta(params):
    try:
        if params['operation'] == 'new':
            del params['operation']
            if params['username'] != 'all':
                params['usuario'] = User.objects.get(username=params['username'])
                del params['username']
                Alerta.objects.create(**params)
            else:
                del params['username']
                usuarios = User.objects.filter(is_active=True)
                for user in usuarios:
                    params['usuario'] = user
                    Alerta.objects.create(**params)
            return [True, 'Alerta <b>criado com successo</b>']
        else:
            return [False, 'Operação <b>inválida</b>']
    except Exception as e:
        return [False, 'Alerta <b>mal formatado</b>, verifique os campos digitados']

def pessoal(request, params):
    try:
        if params['operation'] == 'reengage':
            funcionario = Funcionario.objects.get(matricula=params['matricula'])
            if funcionario.status == 'D':
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
                l.save()
                return [True, 'Cancelado <b>desligamento funcionário</b>']
            else:
                return [False, f'Funcionário <b>{funcionario.matricula}</b> não está desligado']
    except Exception as e:
        return [False, '<b>Operação inválida</b>, verifique os dados digitados']


def usuario(request, params):
    try:
        if params['operation'] == 'global_change_pw':
            qtde = Profile.objects.filter(user__is_active=True, user__is_superuser=False, force_password_change=False).update(force_password_change=True)
            return [True, f'<b>Concluido: {qtde}</b> usuários afetados']
        else:
            return [False, 'Operação <b>inválida</b>']
    except Exception as e:
        return [False, '<b>Operação inválida</b>, verifique os dados digitados']

def globus(request, params):
    try:
        if params['operation'] == 'clean':
            escalas = Escala.objects.filter(data__lte=params['until']).delete()
            return [True, '<b>Concluido</b> limpeza das escalas']
        else:
            return [False, 'Operação <b>inválida</b>']
    except Exception as e:
        return [False, '<b>Operação inválida</b>, verifique os dados digitados']

def runScript(request, params):
    try:
        if params['code'] == '666':
            return [True, 'Nenhum erro, mais <b>nada</b> a fazer']
        else:
            return [False, 'Código de script <b>inválido ou expirado</b>']
    except Exception as e:
        return [False, 'Script mal formatado, verifique os dados lançados']