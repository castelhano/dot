from django.shortcuts import render, redirect
# from django.http import HttpResponse
# from json import dumps
from .models import Veiculo, Area, Vaga, Visitante, RegistroFuncionario, RegistroVisitante
from .forms import VeiculoForm, AreaForm, VagaForm, VisitanteForm, RegistroFuncionarioForm, RegistroVisitanteForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from core.models import Log


# METODOS SHOW
@login_required
@permission_required('portaria.view_veiculo', login_url="/handler/403")
def movimentacao(request):
    return render(request, 'portaria/movimentacao.html')

@login_required
@permission_required('portaria.view_veiculo', login_url="/handler/403")
def veiculos(request):
    veiculos = Veiculo.objects.all().order_by('modelo')
    return render(request,'portaria/veiculos.html', {'veiculos' : veiculos})

@login_required
@permission_required('portaria.view_area', login_url="/handler/403")
def areas(request):
    areas = Vaga.objects.all().order_by('nome')
    return render(request,'portaria/areas.html', {'areas' : areas})

@login_required
@permission_required('portaria.view_vaga', login_url="/handler/403")
def vagas(request):
    vagas = Vaga.objects.all().order_by('codigo')
    return render(request,'portaria/vagas.html', {'vagas' : vagas})

@login_required
@permission_required('portaria.view_visitante', login_url="/handler/403")
def visitantes(request):
    visitantes = Visitante.objects.all().order_by('nome')
    return render(request,'portaria/visitantes.html', {'visitantes' : visitantes})    

@login_required
@permission_required('portaria.view_registro', login_url="/handler/403")
def registros(request):
    tipo = request.GET.get('tipo', None)
    if not request.user.has_perm(f'portaria.view_registro{tipo}'):
        return redirect('handler', 403)
    target_id = request.GET.get('target_id', None)
    if tipo == 'funcionario':
        registros = RegistroFuncionario.objects.filter(veiculo__funcionario__id=target_id).order_by('-data_entrada','-hora_entrada')
    elif tipo == 'visitante':
        registros = RegistroVisitante.objects.filter(visitante__id=target_id).order_by('-data_entrada','-hora_entrada')
    return render(request,'portaria/registros.html', {'registros' : registros})    
        
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
                messages.success(request,'Vaga criada')
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
                l = Log()
                l.modelo = "portaria.visitante"
                l.objeto_id = registro.id
                l.objeto_str = registro.cpf
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Visitante cadastrado')
                return redirect('portaria_visitante_add')
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
        tipo = request.POST['tipo']
        if tipo == 'visitante':
            form = RegistroVisitanteForm(request.POST)
        elif tipo == 'funcionario':
            form = RegistroFuncionarioForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                if registro.vaga != None:
                    vaga = registro.vaga
                    vaga.reservar()
                    vaga.save()
                l = Log()
                l.modelo = f"portaria.registro{tipo}"
                l.objeto_id = registro.id
                l.objeto_str = registro.visitante.cpf if tipo == 'visitante' else registro.veiculo.placa
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Entrada {tipo} inserida')
                return redirect('portaria_movimentacao')
            except:
                messages.error(request,'Erro ao inserir registro visitante [INVALID FORM]')
                return redirect('portaria_movimentacao')

    else:
        form = VisitanteForm()
        return render(request,'portaria/registro_add.html', {'form':form})


# METODOS GET
@login_required
@permission_required('portaria.change_veiculo', login_url="/handler/403")
def veiculo_id(request,id):
    veiculo = Veiculo.objects.get(pk=id)
    form = VeiculoForm(instance=veiculo)
    return render(request,'portaria/veiculo_id.html',{'form':form,'veiculo':veiculo})

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
        form = RegistroVisitanteForm(instance=registro)
    elif tipo == 'funcionario':
        registro = RegistroFuncionario.objects.get(pk=id)
        form = RegistroFuncionarioForm(instance=registro)
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
        messages.success(request,'Vaga alterada')
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
        l = Log()
        l.modelo = "portaria.visitante"
        l.objeto_id = registro.id
        l.objeto_str = registro.cpf
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Visitante alterado')
        return redirect('portaria_visitante_id', id)
    else:
        return render(request,'portaria/visitante_id.html',{'form':form,'visitante':visitante})

# @login_required
# @permission_required('portaria.change_visitante', login_url="/handler/403")
# def visitante_bloquear(request,id):
#     visitante = Visitante.objects.get(pk=id)
#     l = Log()
#     if visitante.bloqueado:
#         visitante.bloqueado = False
#         l.mensagem = "LIBERADO"
#     else:
#         visitante.bloqueado = True
#         l.mensagem = "BLOQUEADO"
#     visitante.save()
#     l.modelo = "portaria.visitante"
#     l.objeto_id = visitante.id
#     l.objeto_str = visitante.cpf
#     l.usuario = request.user
#     l.save()
#     messages.success(request,'Visitante alterado')
#     return redirect('portaria_visitante_id', id)

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
# @login_required
# def get_visitante(request):
#     try:
#         visitante_key = request.GET.get('visitante_key',None)
#         if len(visitante_key) < 14:
#             visitante = Visitante.objects.get(id=visitante_key)
#         else:
#             visitante = Visitante.objects.get(cpf=visitante_key)
#         url = str(visitante.foto.url) if visitante.foto else ''
#         return HttpResponse(str(visitante.id) + ';' + visitante.nome + ';' + str(not visitante.bloqueado) + ';' + url)
#     except:
#         return HttpResponse('')

# @login_required
# def get_veiculo(request):
#     try:
#         veiculo_key = request.GET.get('veiculo_key',None)
#         if len(veiculo_key) < 7:
#             veiculo = Veiculo.objects.get(id=veiculo_key)
#         else:
#             veiculo = Veiculo.objects.get(placa=veiculo_key)
#         return HttpResponse(str(veiculo.id) + ';' + veiculo.funcionario.nome + ';' + veiculo.modelo + ';' + str(veiculo.ativo()))
#     except:
#         return HttpResponse('')

# @login_required
# def get_vaga(request):
#     try:
#         codigo = request.GET.get('codigo',None)
#         vaga = Vaga.objects.get(codigo=codigo, inativa=False)
#         status = 'L' if vaga.disponivel() else 'O'
#         return HttpResponse(str(vaga.id) + ';' + status)
#     except:
#         return HttpResponse('')