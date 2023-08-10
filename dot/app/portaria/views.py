from django.shortcuts import render, redirect
from django.http import HttpResponse
from json import dumps as json_dumps
from .models import Veiculo, Area, Vaga, Visitante, RegistroFuncionario, RegistroVisitante
from .forms import VeiculoForm, AreaForm, VagaForm, VisitanteForm, EntradaFuncionarioForm, SaidaFuncionarioForm, EntradaVisitanteForm, SaidaVisitanteForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from core.models import Log
from django.conf import settings
from core.extras import create_image
from datetime import datetime


# METODOS SHOW
@login_required
@permission_required('portaria.view_veiculo', login_url="/handler/403")
def movimentacao(request):
    areas = Area.objects.all().order_by('nome')
    return render(request, 'portaria/movimentacao.html', {'areas':areas})

@login_required
@permission_required('portaria.view_veiculo', login_url="/handler/403")
def veiculos(request):
    veiculos = Veiculo.objects.all().order_by('modelo')
    return render(request,'portaria/veiculos.html', {'veiculos' : veiculos})

@login_required
@permission_required('portaria.view_vaga', login_url="/handler/403")
def vagas(request):
    areas = Area.objects.all().order_by('nome')
    return render(request,'portaria/vagas.html', {'areas' : areas})

@login_required
@permission_required('portaria.view_visitante', login_url="/handler/403")
def visitantes(request):
    visitantes = Visitante.objects.all().order_by('nome')
    return render(request,'portaria/visitantes.html', {'visitantes' : visitantes})    

@login_required
@permission_required('portaria.view_registro', login_url="/handler/403")
def registros(request):
    ativo = request.GET.get('ativo', True)  # Se True (ou nao informado), exibe apenas os registros sem saida (ainda ativos)
    tipo = request.GET.get('tipo', None)     # Recebe f (default) para registro de funcionario ou v para visitante 
    qs = {}
    if not tipo or tipo == 'f':
        qs['registrosFuncionario'] = RegistroFuncionario.objects.filter(data_saida=None).order_by('data_entrada','hora_entrada')
    if not tipo or tipo == 'v':
        qs['registrosVisitante'] = RegistroVisitante.objects.filter(data_saida=None).order_by('data_entrada','hora_entrada')
    
    # if not request.user.has_perm(f'portaria.view_registro{tipo}'):
    #     return redirect('handler', 403)
    # target_id = request.GET.get('target_id', None)
    # if tipo == 'funcionario':
    #     registros = RegistroFuncionario.objects.filter(veiculo__funcionario__id=target_id).order_by('-data_entrada','-hora_entrada')
    # elif tipo == 'visitante':
    #     registros = RegistroVisitante.objects.filter(visitante__id=target_id).order_by('-data_entrada','-hora_entrada')
    return render(request,'portaria/registros.html', qs)    
        
# METODOS ADD
@login_required
@permission_required('portaria.add_veiculo', login_url="/handler/403")
def veiculo_add(request):
    if request.method == 'POST':
        form = VeiculoForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "portaria.veiculo"
                l.objeto_id = registro.id
                l.objeto_str = registro.placa
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Veiculo criado')
                return redirect('portaria_veiculo_add')
            except:
                messages.error(request,'Erro ao inserir veiculo [INVALID FORM]')
                return redirect('portaria_veiculo_add')
    else:
        form = VeiculoForm()
    return render(request,'portaria/veiculo_add.html',{'form':form})

@login_required
@permission_required('portaria.add_area', login_url="/handler/403")
def area_add(request):
    if request.method == 'POST':
        form = AreaForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "portaria.area"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Área <b>{registro.nome}</b> criada')
                return redirect('portaria_area_add')
            except:
                messages.error(request,'Erro ao inserir area [INVALID FORM]')
                return redirect('portaria_area_add')
    else:
        form = AreaForm()
    return render(request,'portaria/area_add.html',{'form':form})

@login_required
@permission_required('portaria.add_vaga', login_url="/handler/403")
def vaga_add(request):
    if request.method == 'POST':
        form = VagaForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "portaria.vaga"
                l.objeto_id = registro.id
                l.objeto_str = registro.codigo
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Vaga <b>{registro.codigo}</b> criada')
                return redirect('portaria_vaga_add')
            except:
                messages.error(request,'Erro ao inserir vaga [INVALID FORM]')
                return redirect('portaria_vaga_add')
    else:
        form = VagaForm()
    return render(request,'portaria/vaga_add.html',{'form':form})

@login_required
@permission_required('portaria.add_visitante', login_url="/handler/403")
def visitante_add(request):
    if request.method == 'POST':
        form = VisitanteForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                registro = form.save()
                has_warnings = False
                if request.POST['foto_data_url'] != '':
                    prefix = '%s_%s' %(registro.id, registro.nome.split(' ')[0].lower())
                    today = datetime.now()
                    timestamp = datetime.timestamp(today)
                    file_name = f'{prefix}_{timestamp}.png'
                    result = create_image(request.POST['foto_data_url'], f'{settings.MEDIA_ROOT}/portaria/visitante', file_name, f'{prefix}_')
                    if result[0]:
                        registro.foto = f'portaria/visitante/{file_name}'
                        registro.save()
                    else:
                        has_warnings = True
                        messages.warning(request,'<b>Erro ao salvar foto:</b> ' + result[1])
                l = Log()
                l.modelo = "portaria.visitante"
                l.objeto_id = registro.id
                l.objeto_str = registro.cpf
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                if not has_warnings:
                    messages.success(request,f'Visitante <b>{registro.cpf}</b> cadastrado')
                return redirect('portaria_visitante_id', registro.id)
            except:
                messages.error(request,'Erro ao inserir visitante [INVALID FORM]')
                return redirect('portaria_visitante_add')
    else:
        form = VisitanteForm()
    return render(request,'portaria/visitante_add.html',{'form':form})

@login_required
@permission_required('portaria.add_registro', login_url="/handler/403")
def registro_add(request):
    if request.method == 'POST':
        sentido = request.POST['sentido']   # entrada ou saida
        tipo = request.POST['tipo']         # visitante ou funcionario
        if sentido == 'saida':
            vaga = Vaga.objects.get(id=request.POST['vaga'])
            ocupante = vaga.ocupante()
            if isinstance(ocupante, RegistroFuncionario):
                form = SaidaFuncionarioForm(request.POST, instance=ocupante)
                tipo = 'funcionario'
            elif isinstance(ocupante, RegistroVisitante):
                form = SaidaVisitanteForm(request.POST, instance=ocupante)
                tipo = 'visitante'
            else:
                messages.error(request, '<b>Erro:</b> ao identificar ocupante da vaga, procure o administrador')
                return redirect('portaria_movimentacao')
        else:
            if tipo == 'visitante':
                form = EntradaVisitanteForm(request.POST)
            elif tipo == 'funcionario':
                form = EntradaFuncionarioForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save(commit=False)
                if sentido == 'entrada' and tipo == 'funcionario' and RegistroFuncionario.objects.filter(veiculo=registro.veiculo, data_saida=None).exists():
                    messages.error(request,f'<b>Atenção:</b> Veículo já alocado <b>em outra vaga</b>, operação cancelada')
                    return redirect('portaria_movimentacao')
                elif sentido == 'entrada' and tipo == 'visitante' and RegistroVisitante.objects.filter(visitante=registro.visitante, data_saida=None).exists():
                    messages.error(request,f'<b>Atenção:</b> Visitante já alocado <b>em outra vaga</b>, operação cancelada')
                    return redirect('portaria_movimentacao')
                vaga = registro.vaga
                if sentido == 'entrada':
                    retorno = vaga.reservar() # Marca vaga como ocupada (se possivel, caso nao gera [False, 'msg...'] como retorno)
                else:
                    retorno = vaga.desocupar() # Marca vaga como livre (se possivel, caso nao gera [False, 'msg...'] como retorno)
                if not retorno[0]:
                    messages.error(request,f'<b>Atenção:</b> {retorno[1]}, operação cancelada')
                    return redirect('portaria_movimentacao')
                registro.save()
                vaga.save()
                l = Log()
                l.modelo = 'portaria.visitante' if tipo == 'visitante' else 'portaria.veiculo'
                l.objeto_id = registro.ocupante_id() if tipo == 'visitante' else registro.veiculo.id
                l.objeto_str = registro.visitante.cpf if tipo == 'visitante' else registro.veiculo.placa
                l.usuario = request.user
                l.mensagem = sentido.upper()
                l.save()
                messages.success(request,'<b>%s %s</b> registrada' %(sentido.capitalize(), tipo))
            except:
                messages.error(request,'Erro ao inserir registro visitante [GENERIC ERROR]')
        else:
            messages.error(request,'<b>Dados inválidos</b>, verifique as informações lançadas e tente novamente')
        return redirect('portaria_movimentacao')
    else:
        return render(request,'portaria/movimentacao.html')


# METODOS GET
@login_required
@permission_required('portaria.change_veiculo', login_url="/handler/403")
def veiculo_id(request,id):
    veiculo = Veiculo.objects.get(pk=id)
    form = VeiculoForm(instance=veiculo)
    return render(request,'portaria/veiculo_id.html',{'form':form,'veiculo':veiculo})

@login_required
@permission_required('portaria.change_area', login_url="/handler/403")
def area_id(request,id):
    area = Area.objects.get(pk=id)
    form = AreaForm(instance=area)
    return render(request,'portaria/area_id.html',{'form':form,'area':area})

@login_required
@permission_required('portaria.change_vaga', login_url="/handler/403")
def vaga_id(request,id):
    vaga = Vaga.objects.get(pk=id)
    form = VagaForm(instance=vaga)
    return render(request,'portaria/vaga_id.html',{'form':form,'vaga':vaga})

@login_required
@permission_required('portaria.change_visitante', login_url="/handler/403")
def visitante_id(request,id):
    visitante = Visitante.objects.get(pk=id)
    form = VisitanteForm(instance=visitante)
    return render(request,'portaria/visitante_id.html',{'form':form,'visitante':visitante})

@login_required
@permission_required('portaria.change_registro', login_url="/handler/403")
def registro_id(request, id):
    tipo = request.GET['tipo']
    if tipo == 'visitante':
        registro = RegistroVisitante.objects.get(pk=id)
        form = EntradaVisitanteForm(instance=registro)
    elif tipo == 'funcionario':
        registro = RegistroFuncionario.objects.get(pk=id)
        form = EntradaFuncionarioForm(instance=registro)
    vagas = Vaga.objects.filter(inativa=False).order_by('codigo')
    return render(request,'portaria/registro_id.html',{'form':form,'registro':registro,'vagas':vagas})

# METODOS UPDATE
@login_required
@permission_required('portaria.change_veiculo', login_url="/handler/403")
def veiculo_update(request,id):
    veiculo = Veiculo.objects.get(pk=id)
    form = VeiculoForm(request.POST, instance=veiculo)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "portaria.veiculo"
        l.objeto_id = registro.id
        l.objeto_str = registro.placa
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Veiculo alterado')
        return redirect('portaria_veiculo_id', id)
    else:
        return render(request,'portaria/veiculo_id.html',{'form':form,'veiculo':veiculo})

@login_required
@permission_required('portaria.change_area', login_url="/handler/403")
def area_update(request,id):
    area = Area.objects.get(pk=id)
    form = AreaForm(request.POST, instance=area)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "portaria.area"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Área <b>{registro.nome}</b> alterada')
        return redirect('portaria_area_id', id)
    else:
        return render(request,'portaria/area_id.html',{'form':form,'area':area})

@login_required
@permission_required('portaria.change_vaga', login_url="/handler/403")
def vaga_update(request,id):
    vaga = Vaga.objects.get(pk=id)
    form = VagaForm(request.POST, instance=vaga)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "portaria.vaga"
        l.objeto_id = registro.id
        l.objeto_str = registro.codigo
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Vaga <b>{registro.codigo}</b> alterada')
        return redirect('portaria_vaga_id', id)
    else:
        return render(request,'portaria/vaga_id.html',{'form':form,'vaga':vaga})

@login_required
@permission_required('portaria.change_visitante', login_url="/handler/403")
def visitante_update(request,id):
    visitante = Visitante.objects.get(pk=id)
    form = VisitanteForm(request.POST, request.FILES, instance=visitante)
    if form.is_valid():
        registro = form.save()
        has_warnings = False
        if request.POST['foto_data_url'] != '':
            prefix = '%s_%s' %(registro.id, registro.nome.split(' ')[0].lower())
            today = datetime.now()
            timestamp = datetime.timestamp(today)
            file_name = f'{prefix}_{timestamp}.png'
            result = create_image(request.POST['foto_data_url'], f'{settings.MEDIA_ROOT}/portaria/visitante', file_name, f'{prefix}_')
            if result[0]:
                registro.foto = f'portaria/visitante/{file_name}'
                registro.save()
            else:
                has_warnings = True
                messages.warning(request,'<b>Erro ao salvar foto:</b> ' + result[1])
        l = Log()
        l.modelo = "portaria.visitante"
        l.objeto_id = registro.id
        l.objeto_str = registro.cpf
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        if not has_warnings:
            messages.success(request,f'Visitante <b>{registro.cpf}</b> alterado')
        return redirect('portaria_visitante_id', id)
    else:
        return render(request,'portaria/visitante_id.html',{'form':form,'visitante':visitante})

@login_required
@permission_required('portaria.change_registro', login_url="/handler/403")
def registro_update(request,id):
    tipo = request.POST['tipo']
    if tipo == 'visitante':
        pre_registro = RegistroVisitante.objects.get(pk=id)
        form = RegistroVisitanteForm(request.POST, instance=pre_registro)
    elif tipo == 'funcionario':
        pre_registro = RegistroFuncionario.objects.get(pk=id)
        form = RegistroFuncionarioForm(request.POST, instance=pre_registro)
    vaga_atual = pre_registro.vaga
    if form.is_valid():
        registro = form.save()
        if registro.vaga != vaga_atual:
            if vaga_atual != None:
                vaga_atual.desocupar()
                vaga_atual.save()
            if registro.vaga != None:
                vaga = registro.vaga
                vaga.reservar()
                vaga.save()
        l = Log()
        l.modelo = f"portaria.registro{tipo}"
        l.objeto_id = registro.id
        l.objeto_str = registro.visitante.cpf if tipo == 'visitante' else registro.veiculo.placa
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Registro {tipo} alterado')
        return redirect('portaria_registro_id', id)
    else:
        vagas = Vaga.objects.filter(inativa=False).order_by('codigo')
        return render(request,'portaria/registro_id.html',{'form':form,'registro':registro,'vagas':vagas})

# @login_required
# def registro_saida(request):
#     try:
#         modelo = request.POST['modelo']
#         if modelo == 'visitante':
#             registro = RegistroVisitante.objects.get(pk=request.POST['registro'])
#         elif modelo == 'funcionario':
#             registro = RegistroFuncionario.objects.get(pk=request.POST['registro'])
#         registro.data_saida = request.POST['data_saida']
#         registro.hora_saida = request.POST['hora_saida']
#         if request.POST['km_saida'] != '':
#             registro.km_saida = request.POST['km_saida']
#         registro.save()
#         l = Log()
#         if modelo == 'visitante' and registro.vaga:
#             vaga = registro.vaga
#             vaga.desocupar()
#             vaga.save()
#             l.modelo = "portaria.registrovisitante"
#             l.objeto_str = registro.visitante.cpf
#         else:
#             l.modelo = "portaria.registrofuncionario"            
#             l.objeto_str = registro.veiculo.funcionario.matricula
#         l.modelo = "portaria.registrovisitante"
#         l.objeto_id = registro.id
#         l.usuario = request.user
#         l.mensagem = "SAIDA"
#         l.save()
#         messages.success(request,'Saida registrada')
#     except:
#         messages.error(request,'Erro ao registrar saida')
#     return redirect('portaria_movimentacao')


# METODOS DELETE
@login_required
@permission_required('portaria.delete_veiculo', login_url="/handler/403")
def veiculo_delete(request,id):
    try:
        registro = Veiculo.objects.get(pk=id)
        l = Log()
        l.modelo = "portaria.veiculo"
        l.objeto_id = registro.id
        l.objeto_str = registro.placa
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Veiculo apagado. Essa operação não pode ser desfeita')
        return redirect('portaria_veiculos')
    except:
        messages.error(request,'ERRO ao apagar veiculo')
        return redirect('portaria_veiculo_id', id)

@login_required
@permission_required('portaria.delete_area', login_url="/handler/403")
def area_delete(request,id):
    try:
        registro = Area.objects.get(pk=id)
        l = Log()
        l.modelo = "portaria.area"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Área apagada. Essa operação não pode ser desfeita')
        return redirect('portaria_vagas')
    except:
        messages.error(request,'ERRO ao apagar area')
        return redirect('portaria_area_id', id)

@login_required
@permission_required('portaria.delete_vaga', login_url="/handler/403")
def vaga_delete(request,id):
    try:
        registro = Vaga.objects.get(pk=id)
        l = Log()
        l.modelo = "portaria.vaga"
        l.objeto_id = registro.id
        l.objeto_str = registro.codigo
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Vaga apagada. Essa operação não pode ser desfeita')
        return redirect('portaria_vagas')
    except:
        messages.error(request,'ERRO ao apagar vaga')
        return redirect('portaria_vaga_id', id)

@login_required
@permission_required('portaria.delete_visitante', login_url="/handler/403")
def visitante_delete(request,id):
    try:
        registro = Visitante.objects.get(pk=id)
        l = Log()
        l.modelo = "portaria.visitante"
        l.objeto_id = registro.id
        l.objeto_str = registro.cpf
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Visitante apagado. Essa operação não pode ser desfeita')
        return redirect('portaria_visitantes')
    except:
        messages.error(request,'ERRO ao apagar visitante')
        return redirect('portaria_visitante_id', id)

@login_required
@permission_required('portaria.delete_registro', login_url="/handler/403")
def registro_delete(request,id):
    try:
        tipo = request.GET['tipo']
        if tipo == 'visitante':
            registro = RegistroVisitante.objects.get(pk=id)
        elif tipo == 'funcionario':
            registro = RegistroFuncionario.objects.get(pk=id)
        l = Log()
        l.modelo = f"portaria.registro{tipo}"
        l.objeto_id = registro.id
        l.objeto_str = registro.visitante.cpf if tipo == 'visitante' else registro.veiculo.placa
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        if registro.vaga != '':
            vaga = registro.vaga
            vaga.desocupar()
            vaga.save()
        registro.delete()
        messages.warning(request,f'Registro {tipo} apagado. Essa operação não pode ser desfeita')
        return redirect('portaria_movimentacao')
    except:
        messages.error(request,'ERRO ao apagar registro')
        return redirect('portaria_registro_id', id)

# METODOS AJAX
@login_required
def get_visitante(request):
    try:
        visitante = Visitante.objects.get(cpf=request.GET['cpf'])
        item_dict = vars(visitante) # Gera lista com atributos do visitante
        if visitante.foto:
            item_dict['foto'] = visitante.foto_url()
        else:
            del item_dict['foto']
        if '_state' in item_dict: del item_dict['_state'] # Remove _state do dict (se existir)
        dataJSON = json_dumps(item_dict)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

@login_required
def get_veiculo(request):
    try:
        placa = request.GET.get('placa', None)
        veiculo = Veiculo.objects.get(placa=placa)
        item_dict = vars(veiculo) # Gera lista com atributos do veiculo
        item_dict['status'] = 'ATIVO' if veiculo.ativo() else 'VENCIDO'
        item_dict['funcionario'] = veiculo.funcionario.nome
        if veiculo.funcionario.foto:
            item_dict['foto'] = veiculo.funcionario.foto_url()
        if '_state' in item_dict: del item_dict['_state'] # Remove _state do dict (se existir)
        del item_dict['valido_ate'] # Remove data de validade
        dataJSON = json_dumps(item_dict)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

@login_required
def get_ocupante(request):
    try:
        vaga = Vaga.objects.get(id=request.GET['vaga'])
        ocupante = vaga.ocupante()
        item_dict = {}
        if isinstance(ocupante, RegistroFuncionario):
            item_dict['tipo'] = 'FUNCIONARIO'
            item_dict['matricula'] = ocupante.veiculo.funcionario.matricula
            item_dict['nome'] = ocupante.veiculo.funcionario.nome
            item_dict['veiculo'] = ocupante.veiculo.modelo
            item_dict['cor'] = ocupante.veiculo.cor
            item_dict['placa'] = ocupante.veiculo.placa
            item_dict['empresa'] = ocupante.veiculo.funcionario.empresa.nome
            if ocupante.veiculo.funcionario.foto:
                item_dict['foto'] = ocupante.veiculo.funcionario.foto_url()

        if isinstance(ocupante, RegistroVisitante):
            item_dict['tipo'] = 'VISITANTE'
            item_dict['nome'] = ocupante.visitante.nome
            item_dict['veiculo'] = ocupante.modelo
            item_dict['cor'] = ocupante.cor
            item_dict['placa'] = ocupante.placa
            item_dict['empresa'] = ocupante.visitante.empresa
            if ocupante.visitante.foto:
                item_dict['foto'] = ocupante.visitante.foto_url()
        
        item_dict['data_entrada'] = ocupante.data_entrada.strftime("%d/%m/%Y")
        item_dict['hora_entrada'] = ocupante.hora_entrada.strftime("%H:%M")

        dataJSON = json_dumps(item_dict)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')