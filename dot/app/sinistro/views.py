import os
from django.shortcuts import render, redirect
from django.http import HttpResponse
from json import dumps
from .models import Acidente, Foto, Oficina, Classificacao, Terceiro, TipoDespesa, Despesa, Forma, Termo, Paragrafo
from .forms import AcidenteForm, ClassificacaoForm, OficinaForm, TerceiroForm, TipoDespesaForm, DespesaForm, FormaForm, TermoForm
from core.models import Log, Empresa
from oficina.models import Frota
from pessoal.models import Funcionario
from trafego.models import Linha
from django.contrib.auth.decorators import login_required, permission_required
from .validators import validate_file_extension
from django.contrib import messages
from django.db.models import Q, Sum, Count
from datetime import date

# METODOS SHOW
@login_required
@permission_required('sinistro.view_acidente')
def acidentes(request):
    semTerceiros =  Acidente.objects.filter(terceiro__isnull=True).order_by('data')
    terceiros =  Terceiro.objects.all().order_by('acidente__data')
    validado = False
    if request.method == 'POST': 
        if request.POST['pesquisa'] != '':
            if request.POST['pesquisa'][0] == '#' and len(request.POST['pesquisa']) > 1:
                try:
                    sinistro = Acidente.objects.get(pasta=request.POST['pesquisa'][1:])
                    return redirect('sinistro_acidente_id',sinistro.id)
                except:
                     messages.warning(request,'Sinistro não localizado')
                     return render(request,'sinistro/acidentes.html')
            elif len(request.POST['pesquisa']) > 1:
                validado = True
                semTerceiros = semTerceiros.filter(Q(veiculo__prefixo=request.POST['pesquisa']) | Q(veiculo__placa__contains=request.POST['pesquisa']) | Q(condutor__matricula=request.POST['pesquisa']))
                terceiros = terceiros.filter(Q(acidente__veiculo__prefixo=request.POST['pesquisa']) | Q(acidente__veiculo__placa__contains=request.POST['pesquisa']) | Q(nome__contains=request.POST['pesquisa']) | Q(veiculo__contains=request.POST['pesquisa']) | Q(placa__contains=request.POST['pesquisa']) | Q(acidente__condutor__matricula=request.POST['pesquisa']))
        if request.POST['empresa'] != '':
            semTerceiros = semTerceiros.filter(empresa__id=request.POST['empresa'])
            terceiros = terceiros.filter(acidente__empresa__id=request.POST['empresa'])
        if request.POST['inspetor'] != '':
            validado = True
            semTerceiros = semTerceiros.filter(inspetor__id=request.POST['inspetor'])
            terceiros = terceiros.filter(acidente__inspetor__id=request.POST['inspetor'])
        if request.POST['periodo_de'] != '' and request.POST['periodo_ate'] != '':
            validado = True
            semTerceiros = semTerceiros.filter(data__range=(request.POST['periodo_de'],request.POST['periodo_ate']))
            terceiros = terceiros.filter(acidente__data__range=(request.POST['periodo_de'],request.POST['periodo_ate']))
        if request.POST['concluido'] != '':
            concluido = True if request.POST['concluido'] == 'True' else False
            if not concluido: # Permite pesquisa dos acidentes em aberto, porem para filtar concluidos eh necessario ter filtrado em outro criterio anterior
                validado = True
            semTerceiros = semTerceiros.filter(concluido=concluido)
            terceiros = terceiros.filter(acidente__concluido=concluido)
        if request.POST['culpabilidade'] != 'ALL':
            semTerceiros = semTerceiros.filter(culpabilidade=request.POST['culpabilidade'])
            terceiros = terceiros.filter(acidente__culpabilidade=request.POST['culpabilidade'])
        if request.POST['status_terceiro'] != '':
            semTerceiros = None
            status = True if request.POST['status_terceiro'] == 'True' else False
            if not status: # Permite pesquisa dos terceiros em aberto, porem para filtar concluidos eh necessario ter filtrado em outro criterio anterior
                validado = True
            terceiros = terceiros.filter(concluido=status)
        if not validado:
            messages.warning(request,'Informe um criterio para pesquisa')
            return render(request,'sinistro/acidentes.html')
    else:
        semTerceiros = semTerceiros.filter(concluido=False)
        terceiros = terceiros.filter(concluido=False)    
    return render(request,'sinistro/acidentes.html',{'terceiros':terceiros,'semTerceiros':semTerceiros})


@login_required
@permission_required('sinistro.view_classificacao')
def classificacoes(request):
    classificacoes = Classificacao.objects.all().order_by('nome')
    if request.method == 'POST' and request.POST['pesquisa'] != '':
        classificacoes = classificacoes.filter(nome__contains=request.POST['pesquisa'])
    return render(request,'sinistro/classificacoes.html', {'classificacoes' : classificacoes})

@login_required
@permission_required('sinistro.view_oficina')
def oficinas(request):
    oficinas = Oficina.objects.all().order_by('nome')
    if request.method == 'POST':
        if request.POST['pesquisa'] != '':
            oficinas = oficinas.filter(nome__contains=request.POST['pesquisa'])
        if 'ativa' in request.POST:
            oficinas = oficinas.filter(ativa=True)
    else:
        oficinas = oficinas.filter(ativa=True)
    return render(request,'sinistro/oficinas.html', {'oficinas' : oficinas})
    
@login_required
@permission_required('sinistro.view_foto')
def fotos(request, id):
    acidente = Acidente.objects.get(pk=id)
    fotos = Foto.objects.filter(acidente__id=id)
    return render(request,'sinistro/fotos.html', {'fotos':fotos,'acidente':acidente})

@login_required
@permission_required('sinistro.view_terceiro')
def terceiros(request, id):
    acidente = Acidente.objects.get(pk=id)
    terceiros = Terceiro.objects.filter(acidente=acidente)
    if request.method == 'POST':
        terceiros = terceiros.filter(nome__contains=request.POST['pesquisa'])
    form = TerceiroForm()
    return render(request,'sinistro/terceiros.html', {'form':form,'terceiros':terceiros,'acidente':acidente})

@login_required
@permission_required('sinistro.view_tipodespesa')
def tipos_despesa(request):
    tipos_despesa = TipoDespesa.objects.all().order_by('nome')
    if request.method == 'POST' and request.POST['pesquisa'] != '':
        tipos_despesa = tipos_despesa.filter(nome__contains=request.POST['pesquisa'])
    return render(request,'sinistro/tipos_despesa.html', {'tipos_despesa':tipos_despesa})

@login_required
@permission_required('sinistro.view_forma')
def formas(request):
    formas = Forma.objects.all().order_by('nome')
    if request.method == 'POST' and request.POST['pesquisa'] != '':
        formas = formas.filter(nome__contains=request.POST['pesquisa'])
    return render(request,'sinistro/formas.html', {'formas':formas})

@login_required
@permission_required('sinistro.view_despesa')
def despesas(request, terceiro):
    despesas = Despesa.objects.filter(terceiro=terceiro)
    total = despesas.aggregate(Sum('valor'))['valor__sum']
    terceiro = Terceiro.objects.get(id=terceiro)
    return render(request,'sinistro/despesas.html', {'despesas':despesas,'terceiro':terceiro,'total':total})

@login_required
@permission_required('sinistro.view_termo')
def termos(request):
    termos = Termo.objects.all().order_by('nome')
    return render(request,'sinistro/termos.html', {'termos' : termos})

# @login_required
# @permission_required('sinistro.view_termo')
# def paragrafos(request, id):
#     termo = Termo.objects.get(pk=id)
#     paragrafos = Paragrafo.objects.filter(termo=termo).order_by('ordem')
#     last = Paragrafo.objects.filter(termo=termo).count()
#     form = ParagrafoForm(initial={'ordem':last + 1})
#     return render(request,'sinistro/paragrafos.html', {'form':form,'paragrafos' : paragrafos,'termo':termo})


@login_required
@permission_required('sinistro.view_oficina')
def notas_pendentes(request):
    terceiros = Terceiro.objects.filter(pendente_nota_fiscal=True)
    if request.method == 'POST':
        terceiros = terceiros.filter(Q(oficina__nome__contains=request.POST['pesquisa']) | Q(veiculo__contains=request.POST['pesquisa']) | Q(placa__contains=request.POST['pesquisa']))
    total = terceiros.aggregate(Sum('acordo'))['acordo__sum']
    return render(request,'sinistro/notas_pendentes.html', {'terceiros':terceiros,'total':total})

@login_required
@permission_required('sinistro.view_termo')
def termo_fields(request):
    return render(request,'sinistro/termo_fields.html')
    
# METODOS ADD
@login_required
@permission_required('sinistro.add_acidente')
def acidente_add(request):
    if request.method == 'POST':
        form = AcidenteForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save(commit=False)
                registro.created_on = date.today()
                registro.created_by = request.user
                registro.save()
                l = Log()
                l.modelo = "sinistro.acidente"
                l.objeto_id = registro.id
                l.objeto_str = 'PASTA: ' + str(registro.pasta)[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Acidente <b>{registro.pasta}</b> inserido')
                return redirect('sinistro_acidente_id',registro.id)
            except:
                pass
    else:
        ultima_pasta = Acidente.objects.all().last().pasta
        if ultima_pasta.isdecimal(): # Caso info de pasta seja somente numero, sugere o nome da proxima pasta
            form = AcidenteForm(initial={'pasta':f'{int(ultima_pasta) + 1}'})
        else:
            form = AcidenteForm()
    return render(request,'sinistro/acidente_add.html',{'form':form})

@login_required
@permission_required('sinistro.add_classificacao')
def classificacao_add(request):
    if request.method == 'POST':
        form = ClassificacaoForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "sinistro.classificacao"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Classificacao <b>{registro.nome}</b> criada')
                return redirect('sinistro_classificacao_add')
            except:
                pass
    else:
        form = ClassificacaoForm()
    return render(request,'sinistro/classificacao_add.html',{'form':form})

@login_required
@permission_required('sinistro.add_oficina')
def oficina_add(request):
    if request.method == 'POST':
        form = OficinaForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "sinistro.oficina"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Oficina <b>{registro.nome}</b> criada')
                return redirect('sinistro_oficinas')
            except:
                pass
    else:
        form = OficinaForm()
    return render(request,'sinistro/oficina_add.html',{'form':form})

@login_required
@permission_required('sinistro.add_foto')
def foto_add(request, id):
    if request.method == 'POST':
        acidente = Acidente.objects.get(id=id)
        for foto in request.FILES.getlist('fotos'):
            if validate_file_extension(foto):
                Foto.objects.create(acidente=acidente,foto=foto)
        l = Log()
        l.modelo = "sinistro.acidente"
        l.objeto_id = acidente.id
        l.objeto_str = acidente.pasta
        l.usuario = request.user
        l.mensagem = "ADD FOTO"
        l.save()
        messages.success(request,'Fotos adicionadas')
        return redirect('sinistro_fotos',acidente.id)
    else:
        messages.error(request,'Operacao invalida')
        return redirect('sinistro_acidentes')

@login_required
@permission_required('sinistro.add_terceiro')
def terceiro_add(request, id):
    if request.method == 'POST':
        form = TerceiroForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "sinistro.terceiro"
                l.objeto_id = registro.id
                l.objeto_str = 'PASTA: ' + registro.acidente.pasta + ' | ' + registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Terceiro <b>{registro.nome}</b> adicionado')
                return redirect('sinistro_terceiro_id',registro.id)
            except:
                pass
    else:
        form = TerceiroForm()
    acidente = Acidente.objects.filter(pk=id).get()
    return render(request,'sinistro/terceiro_add.html',{'form':form,'acidente':acidente})

@login_required
@permission_required('sinistro.view_tipodespesa')
def tipo_despesa_add(request):
    if request.method == 'POST':
        form = TipoDespesaForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "sinistro.tipodespesa"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Despesa <b>{registro.nome}</b> criada')
                return redirect('sinistro_tipo_despesa_add')
            except:
                pass
    else:
        form = TipoDespesaForm()
    return render(request,'sinistro/tipo_despesa_add.html',{'form':form})

@login_required
@permission_required('sinistro.view_forma')
def forma_add(request):
    if request.method == 'POST':
        form = FormaForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "sinistro.forma"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Forma <b>{registro.nome}</b> inserida')
                return redirect('sinistro_forma_add')
            except:
                pass
    else:
        form = FormaForm()
    return render(request,'sinistro/forma_add.html',{'form':form})

@login_required
@permission_required('sinistro.add_despesa')
def despesa_add(request, terceiro):
    if request.method == 'POST':
        form = DespesaForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                messages.success(request,'Despesa adicionada')
                return redirect('sinistro_despesas',terceiro)
            except:
                pass
    else:
        form = DespesaForm()
    # despesas = Despesa.objects.filter(terceiro=terceiro)
    terceiro = Terceiro.objects.get(id=terceiro)
    return render(request,'sinistro/despesa_add.html',{'form':form, 'terceiro':terceiro})

@login_required
@permission_required('sinistro.add_termo')
def termo_add(request):
    if request.method == 'POST':
        form = TermoForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save(commit=False)
                registro.author = request.user
                registro.save()
                l = Log()
                l.modelo = "sinistro.termo"
                l.objeto_id = registro.id
                l.objeto_str = registro.nome[0:48]
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,'Termo criado')
                return redirect('sinistro_termo_id',registro.id)
            except:
                pass
    else:
        form = TermoForm()
    return render(request,'sinistro/termo_add.html',{'form':form})

@login_required
@permission_required('sinistro.add_paragrafo')
def paragrafo_add(request, id):
    if request.method == 'POST':
        try:
            termo = Termo.objects.get(id=id)
            ordem = Paragrafo.objects.filter(termo=termo).count()
            texto = request.POST['texto']
            if ordem < 10:
                Paragrafo.objects.create(termo=termo,ordem=ordem,texto=texto)
                messages.success(request,'Paragrafo inserido')
                return redirect('sinistro_paragrafos',id)
            else:
                messages.warning(request,'Numero máximo de paragrafos adicionados')
                return redirect('sinistro_paragrafos',id)
        except:
            messages.error(request,'Erro ao inserir paragrafo')
            return redirect('sinistro_termo_id',id)
    else:
        termo = Termo.objects.get(id=id)
        return render(request,'sinistro/paragrafo_add.html',{'termo':termo})



# METODOS GET
@login_required
@permission_required('sinistro.view_acidente')
def acidente_id(request, id):
    acidente = Acidente.objects.get(id=id)
    form = AcidenteForm(instance=acidente)
    return render(request,'sinistro/acidente_id.html',{'form':form,'acidente':acidente})

@login_required
@permission_required('sinistro.change_classificacao')
def classificacao_id(request, id):
    classificacao = Classificacao.objects.get(id=id)
    form = ClassificacaoForm(instance=classificacao)
    return render(request,'sinistro/classificacao_id.html',{'form':form,'classificacao':classificacao})

@login_required
@permission_required('sinistro.change_oficina')
def oficina_id(request, id):
    oficina = Oficina.objects.get(id=id)
    form = OficinaForm(instance=oficina)
    return render(request,'sinistro/oficina_id.html',{'form':form,'oficina':oficina})


@login_required
@permission_required('sinistro.change_terceiro')
def terceiro_id(request, id):
    terceiro = Terceiro.objects.get(id=id)
    form = TerceiroForm(instance=terceiro)
    termos = Termo.objects.all()
    return render(request,'sinistro/terceiro_id.html',{'form':form,'terceiro':terceiro,'termos':termos})

@login_required
@permission_required('sinistro.change_tipodespesa')
def tipo_despesa_id(request, id):
    tipo_despesa = TipoDespesa.objects.get(id=id)
    form = TipoDespesaForm(instance=tipo_despesa)
    return render(request,'sinistro/tipo_despesa_id.html',{'form':form,'tipo_despesa':tipo_despesa})

@login_required
@permission_required('sinistro.change_forma')
def forma_id(request, id):
    forma = Forma.objects.get(id=id)
    form = FormaForm(instance=forma)
    return render(request,'sinistro/forma_id.html',{'form':form,'forma':forma})

@login_required
@permission_required('sinistro.change_despesa')
def despesa_id(request, id):
    despesa = Despesa.objects.get(id=id)
    form = DespesaForm(instance=despesa)
    return render(request,'sinistro/despesa_id.html',{'form':form,'despesa':despesa})

@login_required
@permission_required('sinistro.change_termo')
def termo_id(request, id):
    termo = Termo.objects.get(id=id)
    form = TermoForm(instance=termo)
    return render(request,'sinistro/termo_id.html',{'form':form,'termo':termo})

# @login_required
# @permission_required('sinistro.change_paragrafo')
# def paragrafo_id(request, id):
#     paragrafo = Paragrafo.objects.get(id=id)
#     form = ParagrafoForm(instance=paragrafo)
#     return render(request,'sinistro/paragrafo_id.html',{'form':form,'paragrafo':paragrafo})

@login_required
@permission_required('sinistro.view_foto')
def foto_download(request, id):
    foto = Foto.objects.get(pk=id)
    filename = foto.foto.name.split('/')[-1]
    response = HttpResponse(foto.foto)
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    return response
    
# METODOS UPDATE
@login_required
@permission_required('sinistro.change_acidente')
def acidente_update(request, id):
    acidente = Acidente.objects.get(pk=id)
    form = AcidenteForm(request.POST,instance=acidente)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "sinistro.acidente"
        l.objeto_id = registro.id
        l.objeto_str = 'PASTA: ' + str(registro.pasta)[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Acidente <b>{registro.pasta}</b> alterado')
        return redirect('sinistro_acidente_id',registro.id)
    else:
        return render(request,'sinistro/acidente_id.html',{'form':form,'acidente':acidente})

@login_required
@permission_required('sinistro.change_classificacao')
def classificacao_update(request, id):
    classificacao = Classificacao.objects.get(pk=id)
    form = ClassificacaoForm(request.POST, instance=classificacao)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "sinistro.classificacao"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Classificacao <b>{registro.nome}</b> alterada')
        return redirect('sinistro_classificacao_id',registro.id)
    else:
        return render(request,'sinistro/classificacao_id.html',{'form':form,'classificacao':classificacao})

@login_required
@permission_required('sinistro.change_oficina')
def oficina_update(request, id):
    oficina = Oficina.objects.get(pk=id)
    form = OficinaForm(request.POST, instance=oficina)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "sinistro.oficina"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Oficina <b>{registro.nome}</b> alterada')
        return redirect('sinistro_oficina_id',registro.id)
    else:
        return render(request,'sinistro/oficina_id.html',{'form':form,'oficina':oficina})

@login_required
@permission_required('sinistro.change_terceiro')
def terceiro_update(request, id):
    terceiro = Terceiro.objects.get(pk=id)
    form = TerceiroForm(request.POST, instance=terceiro)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "sinistro.terceiro"
        l.objeto_id = registro.id
        l.objeto_str = 'PASTA: ' + registro.acidente.pasta + ' | ' + registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Terceiro <b>{registro.nome}</b> atualizado')
        return redirect('sinistro_terceiro_id', terceiro.id)
    else:
        return render(request,'sinistro/terceiro_id.html',{'form':form,'terceiro':terceiro})

@login_required
@permission_required('sinistro.change_tipodespesa')
def tipo_despesa_update(request, id):
    tipo_despesa = TipoDespesa.objects.get(pk=id)
    form = TipoDespesaForm(request.POST, instance=tipo_despesa)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "sinistro.tipodespesa"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Tipo despesa <b>{registro.nome}</b> alterada')
        return redirect('sinistro_tipo_despesa_id',id)
    else:
        return render(request,'sinistro/tipo_despesa_id.html',{'form':form,'tipo_despesa':tipo_despesa})

@login_required
@permission_required('sinistro.change_forma')
def forma_update(request, id):
    forma = Forma.objects.get(pk=id)
    form = FormaForm(request.POST, instance=forma)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "sinistro.forma"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Forma <b>{registro.nome}</b> alterada')
        return redirect('sinistro_forma_id', forma.id)
    else:
        return render(request,'sinistro/forma_id.html',{'form':form,'forma':forma})

@login_required
@permission_required('sinistro.change_despesa')
def despesa_update(request, id):
    despesa = Despesa.objects.get(pk=id)
    form = DespesaForm(request.POST, instance=despesa)
    if form.is_valid():
        registro = form.save()
        messages.success(request,f'Despesa <b>{registro.nome}</b> alterada')
        return redirect('sinistro_despesas', despesa.terceiro.id)
    else:
        return render(request,'sinistro/despesa_id.html',{'form':form,'despesa':despesa})


@login_required
@permission_required('sinistro.change_termo')
def termo_update(request, id):
    termo = Termo.objects.get(pk=id)
    form = TermoForm(request.POST, instance=termo)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "sinistro.termo"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Termo <b>{registro.nome}</b> alterado')
        return redirect('sinistro_termo_id', id)
    else:
        return render(request,'sinistro/termo_id.html',{'form':form,'termo':termo})

@login_required
@permission_required('sinistro.change_paragrafo')
def paragrafo_update(request, id):
    if request.method == 'POST':
        paragrafo = Paragrafo.objects.get(pk=id)
        paragrafo.texto = request.POST['texto']
        paragrafo.save()    
        l = Log()
        l.modelo = "sinistro.paragrafo"
        l.objeto_id = paragrafo.id
        l.objeto_str = (paragrafo.termo.nome + ' ' + str(paragrafo.ordem))[0:48]
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,'Paragrafo alterado')
        return redirect('sinistro_paragrafos',paragrafo.termo.id)
    else:
        messages.error(request,'Erro')
        return redirect('sinistro_paragrafos',paragrafo.termo.id)

@login_required
@permission_required('sinistro.change_paragrafo')
def paragrafo_up(request, id):
    paragrafo_atual = Paragrafo.objects.get(id=id)
    atual = paragrafo_atual.ordem
    if atual > 0:
        ajustado = atual - 1
        paragrafo_anterior = Paragrafo.objects.get(ordem=ajustado,termo=paragrafo_atual.termo)
        paragrafo_anterior.ordem = atual
        paragrafo_anterior.save()
        paragrafo_atual.ordem = ajustado
        paragrafo_atual.save()
    return redirect('sinistro_paragrafos',paragrafo_atual.termo.id)

@login_required
@permission_required('sinistro.change_paragrafo')
def paragrafo_down(request, id):
    paragrafo_atual = Paragrafo.objects.get(id=id)
    atual = paragrafo_atual.ordem
    size = Paragrafo.objects.filter(termo=paragrafo_atual.termo).count()
    if atual < size - 1:
        ajustado = atual + 1
        paragrafo_posterior = Paragrafo.objects.get(ordem=ajustado,termo=paragrafo_atual.termo)
        paragrafo_posterior.ordem = atual
        paragrafo_posterior.save()
        paragrafo_atual.ordem = ajustado
        paragrafo_atual.save()
    return redirect('sinistro_paragrafos',paragrafo_atual.termo.id)

# METODOS DELETE
@login_required
@permission_required('sinistro.delete_acidente')
def acidente_delete(request, id):
    try:
        registro = Acidente.objects.get(id=id)
        fotos = Foto.objects.filter(acidente=registro)
        for foto in fotos:
            os.remove(foto.foto.path) # REMOVE ARQUIVO FISICO DA FOTO 
        l = Log()
        l.modelo = "sinistro.acidente"
        l.objeto_id = registro.id
        l.objeto_str = 'PASTA: ' + str(registro.pasta)[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Acidente apagado. Essa operação não pode ser desfeita')
        return redirect('sinistro_acidentes')
    except:
        messages.error(request,'ERRO ao apagar acidente')
        return redirect('sinistro_acidente_id', id)

@login_required
@permission_required('sinistro.delete_classificacao')
def classificacao_delete(request, id):
    try:
        registro = Classificacao.objects.get(pk=id)
        l = Log()
        l.modelo = "sinistro.classificacao"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Classificacao apagada. Essa operação não pode ser desfeita')
        return redirect('sinistro_classificacoes')
    except:
        messages.error(request,'ERRO ao apagar classificacao')
        return redirect('sinistro_classificacao_id', id)

@login_required
@permission_required('sinistro.delete_oficina')
def oficina_delete(request, id):
    try:
        registro = Oficina.objects.get(pk=id)
        l = Log()
        l.modelo = "sinistro.oficina"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Oficina apagada. Essa operação não pode ser desfeita')
        return redirect('sinistro_oficinas')
    except:
        messages.error(request,'ERRO ao apagar oficina')
        return redirect('sinistro_oficina_id', id)

@login_required
@permission_required('sinistro.delete_tipodespesa')
def tipo_despesa_delete(request, id):
    try:
        registro = TipoDespesa.objects.get(pk=id)
        l = Log()
        l.modelo = "sinistro.tipodespesa"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Tipo despesa apagada. Essa operação não pode ser desfeita')
        return redirect('sinistro_tipos_despesa')
    except:
        messages.error(request,'ERRO ao apagar tipo despesa')
        return redirect('sinistro_tipo_despesa_id', id)

@login_required
@permission_required('sinistro.delete_forma')
def forma_delete(request, id):
    try:
        registro = Forma.objects.get(pk=id)
        l = Log()
        l.modelo = "sinistro.forma"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Forma apagada. Essa operação não pode ser desfeita')
        return redirect('sinistro_formas')
    except:
        messages.error(request,'ERRO ao apagar forma')
        return redirect('sinistro_forma_id', id)

@login_required
@permission_required('sinistro.delete_foto')
def foto_delete(request, id):
    try:
        registro = Foto.objects.get(pk=id)
        acidente = registro.acidente
        os.remove(registro.foto.path) # REMOVE ARQUIVO FISICO DA FOTO 
        l = Log()
        l.modelo = "sinistro.foto"
        l.objeto_id = registro.id
        l.objeto_str = "PASTA: " + registro.acidente.pasta
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,'Foto removida')
        return redirect('sinistro_fotos',acidente.id)
    except:
        messages.error(request,'ERRO ao apagar foto')
        return redirect('sinistro_acidentes')

@login_required
@permission_required('sinistro.delete_terceiro')
def terceiro_delete(request, id):
    try:
        registro = Terceiro.objects.get(pk=id)
        acidente = registro.acidente
        l = Log()
        l.modelo = "sinistro.terceiro"
        l.objeto_id = registro.id
        l.objeto_str = 'PASTA: ' + registro.acidente.pasta + ' | ' + registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        registro.delete()
        l.save()
        messages.warning(request,f'Terceiro <b>{registro.nome}</b> removido')
        return redirect('sinistro_terceiros',acidente.id)
    except:
        messages.error(request,'ERRO ao apagar terceiro, pois existem lançamentos associados a ele')
        return redirect('sinistro_terceiro_id', id)

@login_required
@permission_required('sinistro.delete_despesa')
def despesa_delete(request, id):
    try:
        registro = Despesa.objects.get(pk=id)
        terceiro = registro.terceiro
        registro.delete()
        messages.warning(request,'Despesa removida')
        return redirect('sinistro_despesas',terceiro.id)
    except:
        messages.error(request,'ERRO ao apagar despesa')
        return redirect('sinistro_acidentes')

@login_required
@permission_required('sinistro.delete_termo')
def termo_delete(request, id):
    try:
        registro = Termo.objects.get(pk=id)
        l = Log()
        l.modelo = "sinistro.termo"
        l.objeto_id = registro.id
        l.objeto_str = registro.nome[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Termo apagado. Essa operação não pode ser desfeita')
        return redirect('sinistro_termos')
    except:
        messages.error(request,'ERRO ao apagar termo')
        return redirect('sinistro_termo_id', id)

@login_required
@permission_required('sinistro.delete_paragrafo')
def paragrafo_delete(request, id):
    try:
        registro = Paragrafo.objects.get(pk=id)
        l = Log()
        l.modelo = "sinistro.paragrafo"
        l.objeto_id = registro.id
        l.objeto_str = (registro.termo.nome + ' ' + str(registro.ordem))[0:48]
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        
        # REORDENA OS PARAGRAFOS
        alvos = Paragrafo.objects.filter(Q(termo=registro.termo.id) & Q(ordem__gt=registro.ordem))
        for alvo in alvos:
            nova_ordem = alvo.ordem - 1
            alvo.ordem = nova_ordem
            alvo.save()
            
        registro.delete()
        messages.warning(request,'Paragrafo apagado. Essa operação não pode ser desfeita')
        return redirect('sinistro_paragrafos', registro.termo.id)
    except:
        messages.error(request,'ERRO ao apagar paragrafo')
        return redirect('sinistro_paragrafo_id', id)


# METODOS AJAX
def get_oficinas(request):
    try:
        oficinas = Oficina.objects.all()
        itens = {}
        for item in oficinas:
            itens[item.nome] = item.id
        dataJSON = dumps(itens)
        return HttpResponse(dataJSON)
    except:
        return HttpResponse('')
