# Monta dicionario com parametros recebidos no request
# --
# @version  1.0
# @since    10/10/2021
# @author   Rafael Gustavo ALves {@email castelhano.rafael@gmail.com }
# @param    {Dict} request Requisicao
# @param    {Array} fields Lista com campos aceitos no request, todos os demais serao desconsiderados
# @returns  {Dict} Dicionario ajustado
def clean_request(request, fields):
    params = {}
    for p in fields:
        if p in request:
            if request[p] != 'True' and request[p] != 'False' and request[p] != 'None':
                params[p] = request[p]
            elif request[p] == 'True':
                params[p] = True
            elif request[p] == 'False':
                params[p] = False
            else:
                params[p] = None
    return params