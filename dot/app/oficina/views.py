from json import dumps
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .models import Frota, Marca, Modelo, Categoria, Classificacao, Componente, Carroceria
from core.models import Log, Empresa
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.db.models import Q
import re
from .forms import FrotaForm, MarcaForm, CategoriaForm, ComponenteForm, ModeloForm, ClassificacaoForm, CarroceriaForm


# METODOS SHOW
@login_required
@permission_required('oficina.view_frota')
def frotas(request):
    if request.method == 'POST':
        frotas = Frota.objects.filter(empresa__in=request.user.profile.empresas.all()).order_by('prefixo')
        validado = False #Precisa informar pelo menos um filtro, ou metodo retorna None
        if(request.POST['pesquisa'] != '' and len(request.POST['pesquisa']) > 2):
            if request.POST['pesquisa'][0] == '#':
                try:
                    veiculo = Frota.objects.get(empresa__in=request.user.profile.empresas.all(), prefixo=request.POST['pesquisa'][1:])
                    return redirect('oficina_frota_id', veiculo.id)
                except:
                    messages.warning(request,'Veiculo não encontrado')
                    return redirect('oficina_frotas')
            else:
                frotas = frotas.filter(placa__contains=request.POST['pesquisa'])
                validado = True
        if request.POST['empresa'] != '':
            frotas = frotas.filter(empresa__id=request.POST['empresa'])
            validado = True
        if request.POST['modelo'] != '':
            frotas = frotas.filter(modelo__id=request.POST['modelo'])
            validado = True
        elif request.POST['marca'] != '':
            frotas = frotas.filter(modelo__marca__id=request.POST['marca'])
            validado = True
        if request.POST['status'] != '':
            frotas = frotas.filter(status=request.POST['status'])
            validado = True
        if request.POST['ano_fabricacao'] != '':
            if request.POST['ano_fabricacao'][0] == '*':
                frotas = frotas.filter(ano_fabricacao__lte=re.sub('\D', '',request.POST['ano_fabricacao']))
                validado = True
            elif request.POST['ano_fabricacao'][-1] == '*':
                frotas = frotas.filter(ano_fabricacao__gte=re.sub('\D', '',request.POST['ano_fabricacao']))
                validado = True
            else:
                frotas = frotas.filter(ano_fabricacao=request.POST['ano_fabricacao'])
                validado = True
        if request.POST['ano_modelo'] != '':
            if request.POST['ano_modelo'][0] == '*':
                frotas = frotas.filter(ano_modelo__lte=re.sub('\D', '',request.POST['ano_modelo']))
                validado = True
            elif request.POST['ano_modelo'][-1] == '*':
                frotas = frotas.filter(ano_modelo__gte=re.sub('\D', '',request.POST['ano_modelo']))
                validado = True
            else:
                frotas = frotas.filter(ano_modelo=request.POST['ano_modelo'])
                validado = True
        if request.POST['componente'] != '':
            frotas = frotas.filter(componentes=request.POST['componente'])
            validado = True
        if not validado:
            frotas = None
            messages.warning(request,'Informe um criterio para a pesquisa')
        elif frotas.count() == 0:
            messages.warning(request,'Nenhum registro com os filtros informados')
            return render(request,'oficina/frotas.html')
        return render(request,'oficina/frotas.html',{'frotas':frotas})
    else:
        return render(request,'oficina/frotas.html')

@login_required
@permission_required('oficina.view_marca')
def marcas(request):
    marcas = Marca.objects.all().order_by('nome')
    if request.method == 'POST':
        marcas = marcas.filter(nome__contains=request.POST['pesquisa'])
    return render(request,'oficina/marcas.html', {'marcas' : marcas})

@login_required
@permission_required('oficina.view_categoria')
def categorias(request):
    categorias = Categoria.objects.all().order_by('nome')
    if request.method == 'POST':
        categorias = categorias.filter(nome__contains=request.POST['pesquisa'])
    return render(request,'oficina/categorias.html', {'categorias' : categorias})

@login_required
@permission_required('oficina.view_componente')
def componentes(request):
    componentes = Componente.objects.all().order_by('nome')
    if request.method == 'POST':
        componentes = componentes.filter(nome__contains=request.POST['pesquisa'])
    return render(request,'oficina/componentes.html', {'componentes' : componentes})

@login_required
@permission_required('oficina.view_classificacao')
def classificacoes(request):
    classificacoes = Classificacao.objects.all().order_by('nome')
    if request.method == 'POST':
        classificacoes = classificacoes.filter(nome__contains=request.POST['pesquisa'])
    return render(request,'oficina/classificacoes.html', {'classificacoes' : classificacoes})

@login_required
@permission_required('oficina.view_carroceria')
def carrocerias(request):
    carrocerias = Carroceria.objects.all().order_by('nome')
    if request.method == 'POST':
        carrocerias = carrocerias.filter(nome__contains=request.POST['pesquisa'])
    return render(request,'oficina/carrocerias.html', {'carrocerias' : carrocerias})

@login_required
@permission_required('oficina.view_modelo')
def modelos(request):
    modelos = Modelo.objects.all().order_by('marca__nome','nome')
    if request.method == 'POST':
        modelos = modelos.filter(Q(nome__contains=request.POST['pesquisa'])|Q(marca__nome__contains=request.POST['pesquisa']))
    return render(request,'oficina/modelos.html', {'modelos' : modelos})

# METODOS ADD
@login_required
@permission_required('oficina.add_frota')
def frota_add(request):
    if request.method == 'POST':
        form = FrotaForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "oficina.frota"
                l.objeto_id = registro.id
                l.objeto_str = registro.prefixo
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Frota <b>' + registro.prefixo + '</b> criada')
                return redirect('oficina_frota_add')
            except:
                pass
    else:
        form = FrotaForm()
    return render(request,'oficina/frota_add.html',{'form':form})

@login_required
@permission_required('oficina.add_marca')
def marca_add(request):
    if request.method == 'POST':
        form = MarcaForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "oficina.marca"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Marca <b>' + registro.nome + '</b> criada')
                return redirect('oficina_marca_add')
            except:
                pass
    else:
        form = MarcaForm()
    return render(request,'oficina/marca_add.html',{'form':form})

@login_required
@permission_required('oficina.add_classificacao')
def classificacao_add(request):
    if request.method == 'POST':
        form = ClassificacaoForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "oficina.classificacao"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Classificação <b>' + registro.nome + '</b> criada')
                return redirect('oficina_classificacao_add')
            except:
                pass
    else:
        form = ClassificacaoForm()
    return render(request,'oficina/classificacao_add.html',{'form':form})

@login_required
@permission_required('oficina.add_categoria')
def categoria_add(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "oficina.categoria"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Categoria <b>' + registro.nome + '<b> criada')
                return redirect('oficina_categoria_add')
            except:
                pass
    else:
        form = CategoriaForm()
    return render(request,'oficina/categoria_add.html',{'form':form})

@login_required
@permission_required('oficina.add_componente')
def componente_add(request):
    if request.method == 'POST':
        form = ComponenteForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "oficina.componente"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Componente <b>' + registro.nome + '<b> criado')
                return redirect('oficina_componente_add')
            except:
                pass
    else:
        form = ComponenteForm()
    return render(request,'oficina/componente_add.html',{'form':form})

@login_required
@permission_required('oficina.add_carroceria')
def carroceria_add(request):
    if request.method == 'POST':
        form = CarroceriaForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "oficina.carroceria"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Carroceria <b>' + registro.nome + '<b> criada')
                return redirect('oficina_carroceria_add')
            except:
                pass
    else:
        form = CarroceriaForm()
    return render(request,'oficina/carroceria_add.html',{'form':form})

@login_required
@permission_required('oficina.add_modelo')
def modelo_add(request):
    if request.method == 'POST':
        form = ModeloForm(request.POST)
        if form.is_valid():
            try:
                registro = form.save()
                l = Log()
                l.modelo = "oficina.modelo"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Modelo <b>' + registro.nome + '<b> criado')
                return redirect('oficina_modelo_add')
            except:
                pass
    else:
        form = ModeloForm()
    return render(request,'oficina/modelo_add.html',{'form':form})
    
# METODOS GET
@login_required
@permission_required('oficina.view_frota')
def frota_id(request, id):
    try:
        frota = Frota.objects.get(empresa__in=request.user.profile.empresas.all(),id=id)
    except:
        messages.warning(request,'Veiculo não encontrado ou não liberado para visualização')
        return redirect('oficina_frotas')
    form = FrotaForm(instance=frota)
    return render(request,'oficina/frota_id.html',{'form':form,'frota':frota})

@login_required
@permission_required('oficina.change_marca')
def marca_id(request, id):
    marca = Marca.objects.get(id=id)
    form = MarcaForm(instance=marca)
    return render(request,'oficina/marca_id.html',{'form':form,'marca':marca})

@login_required
@permission_required('oficina.change_classificacao')
def classificacao_id(request, id):
    classificacao = Classificacao.objects.get(id=id)
    form = ClassificacaoForm(instance=classificacao)
    return render(request,'oficina/classificacao_id.html',{'form':form,'classificacao':classificacao})

@login_required
@permission_required('oficina.change_categoria')
def categoria_id(request, id):
    categoria = Categoria.objects.get(id=id)
    form = CategoriaForm(instance=categoria)
    return render(request,'oficina/categoria_id.html',{'form':form,'categoria':categoria})

@login_required
@permission_required('oficina.change_componente')
def componente_id(request, id):
    componente = Componente.objects.get(id=id)
    form = ComponenteForm(instance=componente)
    return render(request,'oficina/componente_id.html',{'form':form,'componente':componente})

@login_required
@permission_required('oficina.change_carroceria')
def carroceria_id(request, id):
    carroceria = Carroceria.objects.get(id=id)
    form = CarroceriaForm(instance=carroceria)
    return render(request,'oficina/carroceria_id.html',{'form':form,'carroceria':carroceria})

@login_required
@permission_required('oficina.change_modelo')
def modelo_id(request, id):
    modelo = Modelo.objects.get(id=id)
    form = ModeloForm(instance=modelo)
    return render(request,'oficina/modelo_id.html',{'form':form,'modelo':modelo})


# METODOS UPDATE
@login_required
@permission_required('oficina.change_frota')
def frota_update(request, id):
    try:
        frota = Frota.objects.get(empresa__in=request.user.profile.empresas.all(), pk=id)
    except:
        messages.warning(request,'Veiculo não encontrado ou não altorizado para alteração')
    form = FrotaForm(request.POST, request.FILES, instance=frota)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "oficina.frota"
        l.objeto_id = registro.id
        l.objeto_str = registro.prefixo
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Frota <b>' + registro.prefixo + '</b> alterada')
        return redirect('oficina_frota_id',registro.id)
    else:
        return render(request,'oficina/frota_id.html',{'form':form,'frota':frota})

@login_required
@permission_required('oficina.change_frota')
def frota_movimentar(request, id):
    frota = Frota.objects.get(pk=id)
    l = Log()
    if request.GET.get('operacao', None) in ['A', 'I', 'M', 'F']:
        l.mensagem = frota.movimentar(request.GET.get('operacao', None))
    elif request.method == 'POST' and request.GET.get('operacao', None) == 'V' and request.user.has_perm('oficina.vender_frota'):
        args = dict(data_venda=request.POST['data_venda'], comprador=request.POST['comprador'], valor_venda=request.POST['valor_venda'])
        l.mensagem = frota.movimentar('V', **args)
    elif request.GET.get('operacao', None) == 'CV' and request.user.has_perm('oficina.vender_frota'):
        l.mensagem = frota.movimentar('CV')
    else:
        messages.error(request,'Operação não autorizada')
        return redirect('oficina_frota_id', id)        
    frota.save()
    l.modelo = "oficina.frota"
    l.objeto_id = frota.id
    l.objeto_str = frota.prefixo
    l.usuario = request.user
    l.save()
    messages.warning(request,f'Frota <b>{frota.prefixo}</b> {l.mensagem.lower()}')
    return redirect('oficina_frota_id', id)

@login_required
@permission_required('oficina.change_marca')
def marca_update(request, id):
    marca = Marca.objects.get(pk=id)
    form = MarcaForm(request.POST, instance=marca)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "oficina.marca"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Marca <b>' + registro.nome + '</b> alterada')
        return redirect('oficina_marca_id',registro.id)
    else:
        return render(request,'oficina/marca.html',{'form':form,'marca':marca})

@login_required
@permission_required('oficina.change_categoria')
def categoria_update(request, id):
    categoria = Categoria.objects.get(pk=id)
    form = CategoriaForm(request.POST, instance=categoria)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "oficina.categoria"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Categoria <b>' + registro.nome + '</b> alterada')
        return redirect('oficina_categoria_id',registro.id)
    else:
        return render(request,'oficina/categoria.html',{'form':form,'categoria':categoria})

@login_required
@permission_required('oficina.change_componente')
def componente_update(request, id):
    componente = Componente.objects.get(pk=id)
    form = ComponenteForm(request.POST, instance=componente)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "oficina.componente"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Componente ' + registro.nome + ' alterado')
        return redirect('oficina_componente_id',registro.id)
    else:
        return render(request,'oficina/componente.html',{'form':form,'componente':componente})

@login_required
@permission_required('oficina.change_carroceria')
def carroceria_update(request, id):
    carroceria = Carroceria.objects.get(pk=id)
    form = CarroceriaForm(request.POST, instance=carroceria)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "oficina.carroceria"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Carroceria <b>' + registro.nome + '</b> alterado')
        return redirect('oficina_carroceria_id',registro.id)
    else:
        return render(request,'oficina/carroceria.html',{'form':form,'carroceria':carroceria})

@login_required
@permission_required('oficina.change_classificacao')
def classificacao_update(request, id):
    classificacao = Classificacao.objects.get(pk=id)
    form = ClassificacaoForm(request.POST, instance=classificacao)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "oficina.classificacao"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Classificação <b>' + registro.nome + '</b> alterada')
        return redirect('oficina_classificacao_id',registro.id)
    else:
        return render(request,'oficina/classificacao.html',{'form':form,'classificacao':classificacao})

@login_required
@permission_required('oficina.change_modelo')
def modelo_update(request, id):
    modelo = Modelo.objects.get(pk=id)
    form = ModeloForm(request.POST, instance=modelo)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "oficina.modelo"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Modelo <b>' + registro.nome + '</b> alterado')
        return redirect('oficina_modelo_id',registro.id)
    else:
        return render(request,'oficina/modelo.html',{'form':form,'modelo':modelo})

# METODOS DELETE
@login_required
@permission_required('oficina.delete_frota')
def frota_delete(request, id):
    try:
        registro = Frota.objects.get(empresa__in=request.user.profile.empresas.all(), pk=id)
        l = Log()
        l.modelo = "oficina.frota"
        l.objeto_id = registro.id
        l.objeto_str = registro.prefixo
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Frota apagada. Essa operação não pode ser desfeita')
        return redirect('oficina_frotas')
    except:
        messages.error(request,'ERRO ao apagar frota')
        return redirect('oficina_frota_id', id)

@login_required
@permission_required('oficina.delete_marca')
def marca_delete(request, id):
    try:
        registro = Marca.objects.get(pk=id)
        l = Log()
        l.modelo = "oficina.marca"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Marca apagada. Essa operação não pode ser desfeita')
        return redirect('oficina_marcas')
    except:
        messages.error(request,'ERRO ao apagar marca')
        return redirect('oficina_marca_id', id)

@login_required
@permission_required('oficina.delete_classificacao')
def classificacao_delete(request, id):
    try:
        registro = Classificacao.objects.get(pk=id)
        l = Log()
        l.modelo = "oficina.classificacao"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Classificação apagada. Essa operação não pode ser desfeita')
        return redirect('oficina_classificacoes')
    except:
        messages.error(request,'ERRO ao apagar classificação')
        return redirect('oficina_classificacao_id', id)

@login_required
@permission_required('oficina.delete_categoria')
def categoria_delete(request, id):
    try:
        registro = Categoria.objects.get(pk=id)
        l = Log()
        l.modelo = "oficina.categoria"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Categoria apagada. Essa operação não pode ser desfeita')
        return redirect('oficina_categorias')
    except:
        messages.error(request,'ERRO ao apagar categoria')
        return redirect('oficina_categoria_id', id)

@login_required
@permission_required('oficina.delete_componente')
def componente_delete(request, id):
    try:
        registro = Componente.objects.get(pk=id)
        l = Log()
        l.modelo = "oficina.componente"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Componente apagado. Essa operação não pode ser desfeita')
        return redirect('oficina_componentes')
    except:
        messages.error(request,'ERRO ao apagar componente')
        return redirect('oficina_componente_id', id)

@login_required
@permission_required('oficina.delete_carroceria')
def carroceria_delete(request, id):
    try:
        registro = Carroceria.objects.get(pk=id)
        l = Log()
        l.modelo = "oficina.carroceria"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Carroceria apagada. Essa operação não pode ser desfeita')
        return redirect('oficina_carrocerias')
    except:
        messages.error(request,'ERRO ao apagar carroceria')
        return redirect('oficina_carroceria_id', id)

@login_required
@permission_required('oficina.delete_modelo')
def modelo_delete(request, id):
    try:
        registro = Modelo.objects.get(pk=id)
        l = Log()
        l.modelo = "oficina.modelo"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Modelo apagado. Essa operação não pode ser desfeita')
        return redirect('oficina_modelos')
    except:
        messages.error(request,'ERRO ao apagar modelo')
        return redirect('oficina_modelo_id', id)

# -----------------------------------------------------------------------
# VIEWS ADICIONAIS
def get_frota(request):
    try:
        empresa = request.GET.get('empresa',None)
        prefixo = request.GET.get('prefixo',None)
        incluir_inativos = request.GET.get('incluir_inativos',None)
        multiempresa = request.GET.get('multiempresa', None)
        params  = dict(prefixo=prefixo)
        if not multiempresa or multiempresa != 'True':
            params['empresa__id'] = empresa
        frota = Frota.objects.get(**params)
        if incluir_inativos == 'False' and frota.status != 'A':
            raise Exception('')
        return HttpResponse(str(frota.id) + ';' + str(frota.placa) + ';' + str(frota.status))
    except:
        return HttpResponse('')

def get_frota_empresa(request):
    try:
        empresa_id = request.GET.get('empresa',None)
        frota = Frota.objects.filter(empresa__id=empresa,status='A').order_by('prefixo')
        itens = {}
        for item in frota:
            itens[item.prefixo] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

def get_marcas(request):
    try:
        marcas = Marca.objects.all().order_by('nome')
        itens = {}
        for item in marcas:
            itens[item.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

def get_modelos(request):
    try:
        marca_id = request.GET.get('marca',None)
        if marca_id:
            modelos = Modelo.objects.filter(marca__id=marca_id).order_by('nome')
        else:
            modelos = Modelo.objects.all().order_by('nome')
            
        itens = {}
        for item in modelos:
            itens[item.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

def get_componentes(request):
    try:
        componentes = Componente.objects.all().order_by('nome')
        itens = {}
        for item in componentes:
            itens[item.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

def get_categorias(request):
    try:
        categorias = Categoria.objects.all().order_by('nome')
        itens = {}
        for item in categorias:
            itens[item.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

def get_classificacoes(request):
    try:
        classificacoes = Classificacao.objects.all().order_by('nome')
        itens = {}
        for item in classificacoes:
            itens[item.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

def get_frota_placa(request):
    try:
        prefixo = request.GET.get('prefixo',None)
        carro = Frota.objects.get(prefixo=prefixo)
        return HttpResponse(carro.placa)
    except:
        return HttpResponse('')