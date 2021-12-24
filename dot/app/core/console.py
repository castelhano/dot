import re
from .models import Alerta

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
    # try:
        response = ''
        usuario = None
        for attr in attrs:
            errors = False
            mensagem = ''
            if len(attr) == 0: # Ignora espaços em branco entre os atributos
                pass
            elif attr[0] == '#' and not errors: # Atribui usuário ou all 
                username = attr[1:]
                if username == 'all':
                    usuario = 'all'
                else:
                    try:
                        usuario = User.objects.get(username=username)
                        response = f'<b class="text-success">Done:</b> Alert create for user <b class="text-success">{usuario.username}</b>'
                    except:
                        errors = True
                        response = f'<span><b class="text-danger">Error:</b> User <b>{username}</b> nor found, alert not created</span><br />'
            # elif attr[0] == ':' and not errors:
            #     response += f'{attr} Eh um Atributo Field'
            # elif attr[0:1] == '__' and not errors:
            #     response += f'{attr} Eh um Atributo Field'
            # elif not errors: # Entrada não se encaixa em nenhuma das predefinidas, descarta entrada
            #     response += f'{attr} Descartado'
                
        # usuario = User.objects.get(id=1)
        # titulo = 'Alerta com Link'
        # mensagem = 'Verificamos que você eh um <b>merda</b>, favor confirmar esta cnstatacao....'
        # link = 'core_usuarios'
        # alerta = Alerta.objects.create(usuario=usuario, titulo=titulo, mensagem=mensagem, link=link)
        # alerta = Alerta.objects.create(to_user=usuario,from_user=request.user,titulo=titulo2,mensagem=mensagem2,critico=True)
    # except:
    #     response = 'DEU MERDA'
        return response