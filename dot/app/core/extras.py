
# Metodo para preparar request.GET (ou post) em dicionario (usado como criterio em querys)
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