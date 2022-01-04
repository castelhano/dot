from django.shortcuts import render, redirect
from django.http import HttpResponse
from json import dumps
from .models import Setor, Cargo, Funcionario, FuncaoFixa, Afastamento
from .forms import SetorForm, CargoForm, FuncionarioForm, FuncaoFixaForm, AfastamentoForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from core.models import Log


# METODOS SHOW
@login_required
@permission_required('pessoal.view_setor')
def setores(request):
    setores = Setor.objects.all().order_by('nome')
    if request.method == 'POST' and request.POST['pesquisa'] != '':
        setores = setores.filter(nome__contains=request.POST['pesquisa'])
    return render(request,'pessoal/setores.html', {'setores' : setores})

@login_required
@permission_required('pessoal.view_cargo')
def cargos(request):
    if request.method == 'POST':
        cargos = Cargo.objects.all().order_by('nome')
        if request.POST['pesquisa'] != '':
            cargos = cargos.filter(nome__contains=request.POST['pesquisa'])
        if request.POST['setor'] != '':
            cargos = cargos.filter(setor__id=request.POST['setor'])
    else:
        cargos = None
    return render(request,'pessoal/cargos.html',{'cargos':cargos})

@login_required
@permission_required('pessoal.view_funcionario')
def funcionarios(request):
    funcionarios = None
    if request.method == 'POST':
        funcionarios = Funcionario.objects.all().order_by('matricula')
        validado = False #Precisa informar pelo menos um filtro, ou metodo retorna None
        if(request.POST['pesquisa'] != '' and len(request.POST['pesquisa']) > 2):
            if request.POST['pesquisa'][0] == '#':
                try:
                    funcionario = Funcionario.objects.get(matricula=request.POST['pesquisa'][1:])
                    return redirect('pessoal_funcionario_id',funcionario.id)
                except:
                    messages.warning(request,'Funcionario nao localizado')
                    return redirect('pessoal_funcionarios')
            else:
                funcionarios = funcionarios.filter(nome__contains=request.POST['pesquisa'])
                validado = True
        if(request.POST['empresa'] != ''):
                funcionarios = funcionarios.filter(empresa=request.POST['empresa'])
                validado = True
        if(request.POST['regime'] != ''):
            funcionarios = funcionarios.filter(regime=request.POST['regime'])
            validado = True
        if(request.POST['cargo'] != ''):
            funcionarios = funcionarios.filter(cargo=request.POST['cargo'])
            validado = True
        else: # SE JA FILTROU POR CARGO EH DESNECESSARIO FILTRAR POR SETOR
            if(request.POST['setor'] != ''):
                funcionarios = funcionarios.filter(cargo__setor=request.POST['setor'])
                validado = True
        if(request.POST['sexo'] != ''):
            funcionarios = funcionarios.filter(sexo=request.POST['sexo'])
            validado = True
        if(request.POST['status'] != ''):
            funcionarios = funcionarios.filter(status=request.POST['status'])
            validado = True
        if(request.POST['vencimento_cnh'] != ''):
            vencimento_cnh = request.POST['vencimento_cnh']
            funcionarios = funcionarios.filter(cnh_validade__lt=vencimento_cnh).order_by('cnh_validade')
            validado = True
        if not validado:
            funcionarios = None
            messages.warning(request,'Informe um criterio para a pesquisa')
        elif funcionarios.count() == 0:
            messages.warning(request,'Nenhum registro com os filtros informados')
            return render(request,'pessoal/funcionarios.html')
    return render(request,'pessoal/funcionarios.html',{'funcionarios':funcionarios})

@login_required
@permission_required('pessoal.view_afastamento')
def afastamentos(request, id):
    funcionario = Funcionario.objects.get(id=id)
    return render(request,'pessoal/afastamentos.html', {'funcionario' : funcionario})

@login_required
@permission_required('pessoal.view_funcaofixa')
def funcoes_fixas(request):
    funcoes_fixas = FuncaoFixa.objects.all()
    return render(request,'pessoal/funcoes_fixas.html', {'funcoes_fixas' : funcoes_fixas})

# METODOS ADD
@login_required
@permission_required('pessoal.add_setor')
def setor_add(request):
    if request.method == 'POST':
        form = SetorForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "pessoal.setor"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Setor ' + registro.nome + ' criado')
                return redirect('pessoal_setor_add')
            except:
                messages.error(request,'Erro ao inserir setor')
                return redirect('pessoal_setor_add')
    else:
        form = SetorForm()
    return render(request,'pessoal/setor_add.html',{'form':form})
    
@login_required
@permission_required('pessoal.add_cargo')
def cargo_add(request):
    if request.method == 'POST':
        form = CargoForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "pessoal.cargo"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Cargo ' + registro.nome + ' criado')
                return redirect('pessoal_cargo_add')
            except:
                messages.error(request,'Erro ao inserir cargo [INVALID FORM]')
                return redirect('pessoal_cargo_add')
    else:
        form = CargoForm()
    return render(request,'pessoal/cargo_add.html',{'form':form})

@login_required
@permission_required('pessoal.add_funcionario')
def funcionario_add(request):
    if request.method == 'POST':
        form = FuncionarioForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "pessoal.funcionario"
                l.objeto_id = registro.id
                l.objeto_str = registro.matricula + ' - ' + registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Funcionário ' + registro.matricula + ' cadastrado')
                return redirect('pessoal_funcionario_id', registro.id)
            except:
                messages.error(request,'Erro ao inserir funcionario [INVALID FORM]')
                return redirect('pessoal_funcionario_add')
    else:
        form = FuncionarioForm()
    return render(request,'pessoal/funcionario_add.html',{'form':form})

@login_required
@permission_required('pessoal.add_afastamento')
def afastamento_add(request, id):
    if request.method == 'POST':
        form = AfastamentoForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save(commit=False)
                resp = registro.funcionario.afastar()
                if resp[0]:
                    registro.save()
                    l = Log()
                    l.modelo = "pessoal.afastamento"
                    l.objeto_id = registro.id
                    l.objeto_str = registro.funcionario.matricula + ' - ' + registro.funcionario.nome[0:48]
                    l.usuario = request.user
                    l.mensagem = resp[1]
                    l.save()
                    messages.success(request,resp[2])
                else:
                    messages.warning(request,resp[2])
                return redirect('pessoal_afastamentos', registro.funcionario.id)
            except:
                messages.error(request,'Erro ao inserir afastamento [INVALID FORM]')
                return redirect('pessoal_afastamento_add', registro.funcionario.id)
    else:
        form = AfastamentoForm()
        funcionario = Funcionario.objects.get(id=id)
    return render(request,'pessoal/afastamento_add.html',{'form':form,'funcionario':funcionario})

@login_required
@permission_required('pessoal.add_funcaofixa')
def funcao_fixa_add(request):
    if request.method == 'POST':
        form = FuncaoFixaForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "pessoal.funcao_fixa"
                l.objeto_id = registro.id
                l.objeto_str = registro.get_nome_display()
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Função fixa criada')
                return redirect('pessoal_funcoes_fixas')
            except:
                pass
    else:
        form = FuncaoFixaForm()
    cargos = Cargo.objects.all().order_by('nome')
    return render(request,'pessoal/funcao_fixa_add.html',{'form':form,'cargos':cargos})

# METODOS GET
@login_required
@permission_required('pessoal.change_setor')
def setor_id(request,id):
    setor = Setor.objects.get(pk=id)
    form = SetorForm(instance=setor)
    return render(request,'pessoal/setor_id.html',{'form':form,'setor':setor})

@login_required
@permission_required('pessoal.change_cargo')
def cargo_id(request,id):
    cargo = Cargo.objects.get(pk=id)
    form = CargoForm(instance=cargo)
    return render(request,'pessoal/cargo_id.html',{'form':form,'cargo':cargo})

@login_required
@permission_required('pessoal.view_funcionario')
def funcionario_id(request,id):
    funcionario = Funcionario.objects.get(pk=id)
    form = FuncionarioForm(instance=funcionario)
    return render(request,'pessoal/funcionario_id.html',{'form':form,'funcionario':funcionario})

@login_required
@permission_required('pessoal.change_afastamento')
def afastamento_id(request,id):
    afastamento = Afastamento.objects.get(pk=id)
    form = AfastamentoForm(instance=afastamento)
    return render(request,'pessoal/afastamento_id.html',{'form':form,'afastamento':afastamento})

@login_required
@permission_required('pessoal.change_funcaofixa')
def funcao_fixa_id(request, id):
    funcao_fixa = FuncaoFixa.objects.get(id=id)
    form = FuncaoFixaForm(instance=funcao_fixa)
    return render(request,'pessoal/funcao_fixa_id.html',{'form':form,'funcao_fixa':funcao_fixa})

# METODOS UPDATE
@login_required
@permission_required('pessoal.change_setor')
def setor_update(request,id):
    setor = Setor.objects.get(pk=id)
    form = SetorForm(request.POST, instance=setor)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "pessoal.setor"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Setor ' + registro.nome + ' alterado')
        return redirect('pessoal_setor_id', id)
    else:
        return render(request,'pessoal/setor_id.html',{'form':form,'setor':setor})

@login_required
@permission_required('pessoal.change_cargo')
def cargo_update(request,id):
    cargo = Cargo.objects.get(pk=id)
    form = CargoForm(request.POST, instance=cargo)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "pessoal.cargo"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Cargo ' + registro.nome + ' alterado')
        return redirect('pessoal_cargo_id', id)
    else:
        return render(request,'pessoal/cargo_id.html',{'form':form,'cargo':cargo})

@login_required
@permission_required('pessoal.change_funcionario')
def funcionario_update(request,id):
    funcionario = Funcionario.objects.get(pk=id)
    form = FuncionarioForm(request.POST, request.FILES, instance=funcionario)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "pessoal.funcionario"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Funcionario ' + registro.matricula + ' alterado')
        return redirect('pessoal_funcionario_id', id)
    else:
        return render(request,'pessoal/funcionario_id.html',{'form':form,'funcionario':funcionario})

@login_required
@permission_required('pessoal.change_afastamento')
def afastamento_update(request,id):
    afastamento = Afastamento.objects.get(pk=id)
    form = AfastamentoForm(request.POST, instance=afastamento)
    if form.is_valid():
        registro = form.save(commit=False)
        resp = registro.funcionario.afastar()
        if resp[0]:
            registro.save()
            l = Log()
            l.modelo = "pessoal.afastamento"
            l.objeto_id = registro.id
            l.objeto_str = registro.funcionario.matricula + ' - ' + registro.funcionario.nome[0:48]
            l.usuario = request.user
            l.mensagem = resp[1]
            l.save()
            messages.success(request,resp[2])
        else:
            messages.warning(request,resp[2])
        return redirect('pessoal_afastamento_id', id)
    else:
        return render(request,'pessoal/afastamento_id.html',{'form':form,'afastamento':afastamento})

@login_required
@permission_required('pessoal.change_funcaofixa')
def funcao_fixa_update(request, id):
    funcao_fixa = FuncaoFixa.objects.get(pk=id)
    form = FuncaoFixaForm(request.POST, instance=funcao_fixa)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "pessoal.funcao_fixa"
        l.objeto_id = registro.id
        l.objeto_str = registro.get_nome_display()
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Função fixa alterada')
        return redirect('pessoal_funcoes_fixas')
    else:
        return render(request,'pessoal/funcao_fixa_id.html',{'form':form,'funcao_fixa':funcao_fixa})

# METODOS DELETE
@login_required
@permission_required('pessoal.delete_setor')
def setor_delete(request,id):
    try:
        registro = Setor.objects.get(pk=id)
        l = Log()
        l.modelo = "pessoal.setor"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Setor apagado. Essa operação não pode ser desfeita')
        return redirect('pessoal_setores')
    except:
        messages.error(request,'ERRO ao apagar setor')
        return redirect('pessoal_setor_id', id)

@login_required
@permission_required('pessoal.delete_cargo')
def cargo_delete(request,id):
    try:
        registro = Cargo.objects.get(pk=id)
        l = Log()
        l.modelo = "pessoal.cargo"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Cargo apagado. Essa operação não pode ser desfeita')
        return redirect('pessoal_cargos')
    except:
        messages.error(request,'ERRO ao apagar cargo')
        return redirect('pessoal_cargo_id', id)

@login_required
@permission_required('pessoal.delete_funcionario')
def funcionario_delete(request,id):
    try:
        registro = Funcionario.objects.get(pk=id)
        l = Log()
        l.modelo = "pessoal.funcionario"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Funcionario apagado. Essa operação não pode ser desfeita')
        return redirect('pessoal_funcionarios')
    except:
        messages.error(request,'ERRO ao apagar funcionario')
        return redirect('pessoal_funcionario_id', id)

@login_required
@permission_required('pessoal.delete_afastamento')
def afastamento_delete(request,id):
    try:
        registro = Afastamento.objects.get(pk=id)
        registro.delete()
        l = Log()
        l.modelo = "pessoal.afastamento"
        l.objeto_id = registro.id
        l.objeto_str = registro.funcionario.matricula + ' - ' + registro.funcionario.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        messages.warning(request,'Afastamento excluido. Essa operação não pode ser desfeita')
        return redirect('pessoal_afastamentos', registro.funcionario.id)
    except:
        messages.error(request,'ERRO ao apagar afastamento')
        return redirect('pessoal_afastamento_id', id)


@login_required
@permission_required('pessoal.delete_funcaofixa')
def funcao_fixa_delete(request, id):
    try:
        registro = FuncaoFixa.objects.get(id=id)
        l = Log()
        l.modelo = "pessoal.funcao_fixa"
        l.objeto_id = registro.id
        l.objeto_str = registro.get_nome_display()[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Função Fixa apagada. Essa operação não pode ser desfeita')
        return redirect('pessoal_funcoes_fixas')
    except:
        messages.error(request,'ERRO ao apagar função fixa')
        return redirect('pessoal_funcao_fixa_id', id)

# OUTROS METODOS
@login_required
@permission_required('pessoal.desligar_funcionario')
def funcionario_desligar(request):
    if request.method == 'POST':
        # try:
            funcionario = Funcionario.objects.get(pk=request.POST['funcionario_desligar_id'])
            response =  funcionario.desligamento(request.POST['data_desligamento'],request.POST['motivo_desligamento'])
            if response[0]:
                l = Log()
                l.modelo = "pessoal.funcionario"
                l.objeto_id = funcionario.id
                l.objeto_str = funcionario.matricula + ' - ' + funcionario.nome[0:48]
                l.usuario = request.user
                l.mensagem = response[1]
                l.save()
                funcionario.save()
                messages.warning(request,response[2])
            else:
                messages.danger(request,response[1])                
            return redirect('pessoal_funcionario_id', funcionario.id)
        # except:
        #     messages.error(request,'Erro ao desligar funcionário')
        #     return redirect('pessoal_funcionarios')
    else:
        messages.error(request,'Operação não autorizada')
        return redirect('pessoal_funcionarios')
        
@login_required
@permission_required('pessoal.afastar_funcionario')
def funcionario_afastar(request):
    if request.method == 'POST':
        try:
            funcionario = Funcionario.objects.get(pk=request.POST['funcionario_afastar_id'])
            data =  funcionario.afastar()
            if data[0]:
                l = Log()
                l.modelo = "pessoal.funcionario"
                l.objeto_id = funcionario.id
                l.objeto_str = funcionario.matricula + ' - ' + funcionario.nome[0:48]
                l.usuario = request.user
                l.mensagem = data[1]
                l.save()
                funcionario.save()
            messages.warning(request,data[2])
            return redirect('pessoal_funcionario_id', funcionario.id)
        except:
            messages.error(request,'Erro ao afastar funcionário')
            return redirect('pessoal_funcionarios')
    else:
        messages.error(request,'Operação não autorizada')
        return redirect('pessoal_funcionarios')

# METODOS AJAX
@login_required
def get_funcionario(request):
    try:
        empresa = request.GET.get('empresa',None)
        matricula = request.GET.get('matricula',None)
        funcaofixa = request.GET.get('funcaofixa',None)
        incluir_inativos = request.GET.get('incluir_inativos',None)
        if funcaofixa != None:
            funcionario = Funcionario.objects.get(empresa__id=empresa, matricula=matricula, cargo__ffixas__nome=funcaofixa)
        else:
            funcionario = Funcionario.objects.get(empresa__id=empresa, matricula=matricula)
        if incluir_inativos == 'False' and funcionario.status != 'A':
            raise Exception('')
        return HttpResponse(str(funcionario.id) + ';' + str(funcionario.nome) + ';' + str(funcionario.cargo.nome) + ';' + str(funcionario.status))
    except:
        return HttpResponse('')

@login_required
def get_setores(request):
    try:
        setores = Setor.objects.all().order_by('nome')
        itens = {}
        for item in setores:
            itens[item.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

@login_required
def get_funcionarios(request):
    try:
        empresa = request.GET.get('empresa',None)
        funcaofixa = request.GET.get('funcaofixa',None)
        incluir_inativos = request.GET.get('incluir_inativos',None)
        funcionarios = Funcionario.objects.filter(empresa__id=empresa).order_by('nome')
        if funcaofixa != '':
            funcionarios = funcionarios.filter(cargo__ffixas__nome=funcaofixa)
        if incluir_inativos != 'True':
            funcionarios = funcionarios.filter(status='A')
        itens = {}
        for item in funcionarios:
            itens[item.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')

@login_required
def get_cargos(request):
    # try:
        setor = request.GET.get('setor',None)
        cargos = Cargo.objects.filter(setor__id=setor)
        itens = {}
        for item in cargos:
            itens[item.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    # except:
    #     return HttpResponse('')

@login_required
def get_cargos_ff(request): # Busca cargos disponiveis / associados a funcao fixa
    try:
        tipo = request.GET.get('tipo',None)
        if request.GET.get('funcao_fixa',None) == 'new':
            cargos = Cargo.objects.all().order_by('nome')
        else:
            funcao_fixa = FuncaoFixa.objects.get(id=request.GET.get('funcao_fixa',None))
            if tipo == 'disponiveis':
                cargos = Cargo.objects.all().exclude(ffixas=funcao_fixa).order_by('nome')
            elif tipo == 'cadastrados':
                cargos = funcao_fixa.cargos.all().order_by('nome')
            else:
                cargos = None
        itens = {}
        for item in cargos:
            itens[item.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')