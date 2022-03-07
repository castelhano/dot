import csv
import json
from django.shortcuts import render, redirect
from .models import Escala, Viagem
from trafego.models import Linha
from oficina.models import Frota
from pessoal.models import Funcionario
from core.models import Empresa
from .forms import EscalaForm
from core.models import Log
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from datetime import datetime


# METODOS SHOW
@login_required
@permission_required('globus.view_escala')
def escalas(request):
    escalas = Escala.objects.all().order_by('data')
    if request.method == 'POST':
        escalas = Escala.objects.filter(data=request.POST['data']).order_by('data')
    # else:
    #     escalas = None
    return render(request,'globus/escalas.html', {'escalas' : escalas})
    
    

# METODOS ADD
@login_required
@permission_required('globus.add_escala')
def escala_add(request):
    if request.method == 'POST':
        form = EscalaForm(request.POST)
        if form.is_valid():
            try:
                form_clean = form.cleaned_data
                registro = form.save()
                l = Log()
                l.modelo = "globus.escala"
                l.objeto_id = registro.id
                l.objeto_str = registro.funcionario.matricula
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Escala <b>{registro.funcionario.matricula}</b> inserida')
                return redirect('globus_escala_add')
            except:
                pass
    else:
        form = EscalaForm()
    return render(request,'globus/escala_add.html',{'form':form})

@login_required
@permission_required('globus.importar_escala')
def escala_importar(request):
    if request.method == 'POST':
        erros = []
        alertas = []
        row_erros = []
        viagens_importadas = 0
        validado = False
        dados_validados = []
        simular = True if request.POST['simular'] == 'True' else False
        if request.POST['dados_validados'] != '':
            arquivo = json.loads(request.POST['dados_validados'])
        else:
            try:
                arquivo = csv.reader(request.FILES['arquivo'].read().decode('utf8').splitlines(), delimiter=';')
            except:
                messages.error(request,'Arquivo <b>inválido</b>')
                return redirect('globus_escala_importar')
        try:
            empresa = Empresa.objects.get(id=request.POST['empresa'])
        except:
            messages.error(request,'<b>Empresa</b> não encontrada ou não habilitada')
            return redirect('globus_escala_importar')
        ultima_escala = Escala()
        ultima_escala_termino = ''
        escalas_analisadas = [] # Ao importar escala, apaga antigas importacoes (caso existirem)
        for row in arquivo:
            error_stat = False
            try:
                ultima_stamp = f'{ultima_escala.linha}_{ultima_escala.tabela}_{ultima_escala.data}'
                row_stamp = f'{row[0]}_{row[4]}_{datetime.strptime(row[21],"%d/%m/%Y").strftime("%Y-%m-%d")}'
            except:
                messages.error(request,'Formato de <b>arquivo inválido</b>')
                return redirect('globus_escala_importar')
            fields = {}
            if ultima_stamp == row_stamp and ultima_escala.id: # Escala ja criada no ultimo registro
                fields['escala'] = ultima_escala
            else: # Cria nova escala
                if ultima_escala.id != None: # Ajusta final da escala no termino da ultima viagem
                    ultima_escala.termino = ultima_escala_termino
                    ultima_escala.save()
                escala = Escala()
                escala.empresa = empresa
                try:
                    escala.linha = Linha.objects.get(codigo=row[0], empresa=empresa, status='A') if row[0] != '' else None
                except:
                    erros.append(f'Linha {row[0]} não habilitada para empresa {empresa.nome}')
                    error_stat = True
                try:
                    escala.funcionario = Funcionario.objects.get(matricula=(row[23].lstrip('0')), empresa=empresa, status='A') if row[23] != '' else None
                except:
                    erros.append(f'Matricula {row[23]} não habilitada para empresa {empresa.nome}')
                    error_stat = True
                try:
                    escala.veiculo = Frota.objects.get(prefixo=row[22].lstrip('0'), empresa=empresa, status='A') if row[22] != '' else None
                except:
                    erros.append(f'Veiculo {row[22]} não habilitado para empresa {empresa.nome}')
                    error_stat = True
                
                escala.data = datetime.strptime(row[21], "%d/%m/%Y").strftime("%Y-%m-%d") if row[21] != '' else None
                if not error_stat and not simular: # Caso nao tenha erros, cria a escala 
                    escala.inicio = f'{row[17][0:2]}:{row[17][-2:]}' if row[17] != '' else f'{row[11][0:2]}:{row[11][-2:]}'
                    escala.termino = f'{row[12][0:2]}:{row[12][-2:]}'
                    escala.nome_escala = row[2]
                    escala.tabela = row[4]
                    escala.local_pegada = row[5]
                    # Verifica a primeira vez que aparece uma linha se existe escala anterior importada, se sim apaga registros
                    if escala.linha and Escala.objects.filter(linha=escala.linha, data=escala.data).exists() and not f'{row[0]}_{row[21]}' in escalas_analisadas:
                        Escala.objects.filter(linha=escala.linha, data=escala.data).delete()
                    if not f'{row[0]}_{row[21]}' in escalas_analisadas:
                        escalas_analisadas.append(f'{row[0]}_{row[21]}')
                    escala.save()
                    ultima_escala = escala
                    ultima_escala_termino = escala.termino
                    fields['escala'] = escala
                elif simular: # Na simulacao verifica se ja nao existe escala importada para data / linha, se sim gera alerta
                    if escala.linha and Escala.objects.filter(linha=escala.linha, data=escala.data).exists() and not f'{row[0]}_{row[21]}' in escalas_analisadas:
                        alertas.append(f'ATENÇÃO: Escala para linha {row[0]} em {row[21]} será sobregravada')
                    if not f'{row[0]}_{row[21]}' in escalas_analisadas:
                        escalas_analisadas.append(f'{row[0]}_{row[21]}')
            if not error_stat: # Caso nao tenha erros, insere a viagem
                if simular:
                    dados_validados.append(row)
                else:
                    fields['origem'] = row[5]
                    fields['destino'] = row[6]
                    fields['produtiva'] = True if row[9] == '1' else False
                    fields['sentido'] = row[10]
                    fields['inicio'] = f'{row[11][0:2]}:{row[11][-2:]}'
                    fields['termino'] = f'{row[12][0:2]}:{row[12][-2:]}'
                    ultima_escala_termino = fields['termino']
                    fields['extra'] = False
                    Viagem.objects.create(**fields)
                    viagens_importadas += 1
            else:
                row_erros.append(str(row).replace(', ',';').replace('\'','').replace('[','').replace(']',''))
        # Ao termino do for necessario ajustar o termino da ultima escala baseado na ultima linha do arquivo
        if ultima_escala.id:
            ultima_escala.termino = ultima_escala_termino
            ultima_escala.save()
        
        erros = list(dict.fromkeys(erros))  # Remove duplicatas
        erros.sort()                        # Ordena array
        if len(erros) > 0:
            if simular:
                messages.warning(request,f'Identificado <b>{len(erros)}</b> erros\n')
            else:
                messages.warning(request,f'<b>{viagens_importadas}</b> Registros importados, <b>{len(row_erros)}</b> descartados por erro\n')
        else:
            if simular:
                if len(alertas) > 0:
                    messages.warning(request,f'Verifique os <b>alertas</b> antes de importar')
                else:
                    messages.success(request,f'Nenhum erro identificado')
                validado = True
            else:
                messages.success(request,f'Importado com sucesso, total de <b>{viagens_importadas}</b> registros')
        return render(request, 'globus/importar.html',{'erros':erros,'row_erros':row_erros,'alertas':alertas, 'validado':validado, 'dados_validados':json.dumps(dados_validados),'empresa':empresa.id})    
    else:
        return render(request, 'globus/importar.html')


# METODOS GET
@login_required
@permission_required('globus.change_escala')
def escala_id(request, id):
    escala = Escala.objects.get(id=id)
    form = EscalaForm(instance=escala)
    return render(request,'globus/escala_id.html',{'form':form,'escala':escala})

# METODOS UPDATE
@login_required
@permission_required('globus.change_escala')
def escala_update(request, id):
    escala = Escala.objects.get(pk=id)
    form = EscalaForm(request.POST, instance=escala)
    if form.is_valid():
        registro = form.save()
        l = Log()
        l.modelo = "globus.escala"
        l.objeto_id = registro.id
        l.objeto_str = registro.funcionario.matricula
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Escala <b>{registro.funcionario.matricula}</b> alterada')
        return redirect('globus_escala_id', id)
    else:
        return render(request,'globus/escala_id.html',{'form':form,'escala':escala})


# METODOS DELETE
@login_required
@permission_required('globus.delete_escala')
def escala_delete(request, id):
    try:
        registro = Escala.objects.get(pk=id)
        l = Log()
        l.modelo = "globus.escala"
        l.objeto_id = registro.id
        l.objeto_str = registro.funcionario.matricula
        l.usuario = request.user
        l.mensagem = "DELETE"
        l.save()
        registro.delete()
        messages.warning(request,'Escala apagada. Essa operação não pode ser desfeita')
        return redirect('globus_escalas')
    except:
        messages.error(request,'<b>Erro</b> ao apagar escala.')
        return redirect('globus_escala_id', id)