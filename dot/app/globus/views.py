import csv
import json
from django.urls import reverse
from urllib.parse import urlencode
from django.shortcuts import render, redirect
from .models import Escala, Viagem, Settings
from trafego.models import Linha
from oficina.models import Frota
from pessoal.models import Funcionario
from core.models import Empresa
from .forms import EscalaForm, SettingsForm
from core.models import Log
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from datetime import datetime, date


# METODOS SHOW
@login_required
@permission_required('globus.view_escala')
def escalas(request):
    if request.GET.get('data', None):
        data = datetime.strptime(request.GET.get('data', None), '%Y-%m-%d').date()
    else:
        data = date.today()
    
    escalas = Escala.objects.filter(data=data).order_by('funcionario__matricula')
    
    if request.GET.get('empresa', None):
        try:
            if request.user.is_superuser:
                empresa = Empresa.objects.get(id=request.GET.get('empresa', None))
            else:
                empresa = request.user.profile.empresas.filter(id=request.GET.get('empresa', None)).get()
        except:
            messages.error(request,'Empresa <b>não encontrada</b> ou <b>não habilitada</b> para o seu usuário')
            return redirect('globus_escalas')
        escalas = escalas.filter(empresa=empresa)
    else:
        if not request.user.is_superuser:
            escalas = escalas.filter(empresa__in=request.user.profile.empresas.all())
    
    metrics = {
    'data':data,
    'empresa_nome':'Todas' if not request.GET.get('empresa', None) else empresa.nome,
    }
    return render(request,'globus/escalas.html', {'escalas' : escalas, 'metrics':metrics})    


@login_required
@permission_required('globus.consultar_escala')
def consultar_escala(request): # Metodo para buscar a escala do funcionario logado
    try:
        funcionario = Funcionario.objects.get(usuario=request.user)
    except:
        messages.error(request,'Funcionário <b>não parametrizado</b>, entre em contato com o administrador')
        return redirect('index')
    try:
        settings = Settings.objects.filter(empresa=funcionario.empresa).get() # Carrega conficuracoes do app
        if request.GET.get('data', None):
            data_consulta = datetime.strptime(request.GET['data'],'%Y-%m-%d').date()
        else:
            data_consulta = date.today()
            
        if settings.consulta_escala_inicio <= data_consulta <= settings.consulta_escala_fim: # Verifica se a data de consulta esta no periodo liberado
            escalas = Escala.objects.filter(funcionario=funcionario,data=data_consulta).order_by('inicio')
        else:
            escalas = None
    except: # Gera excecao caso nao exista confuguracao de pesquisa para empresa
        escalas = None
        data_consulta = None
        settings = None
    return render(request,'globus/consulta_escala.html',{'funcionario':funcionario,'escalas':escalas,'data_consulta':data_consulta, 'settings':settings})

@login_required
@permission_required('globus.localizar_escala')
def localizar_escala(request): # Metodo para localizar a escala de um determinado funcionario ou carro
    if request.method == 'POST':
        try:
            data_consulta = datetime.strptime(request.POST['data'],'%Y-%m-%d').date()
            if request.user.is_superuser: # Filtra as empresas habilitadas para o usuario
                escalas = Escala.objects.filter(data=data_consulta).order_by('inicio')
            else:
                escalas = Escala.objects.filter(data=data_consulta, empresa__in=request.user.profile.empresas.all()).order_by('inicio')
            tipo = request.POST['tipo']
            if tipo == 'funcionario':
                escalas = escalas.filter(funcionario__matricula=request.POST['funcionario'])
            elif tipo == 'veiculo':
                escalas = escalas.filter(veiculo__prefixo=request.POST['veiculo'])
            else:
                escalas = None
        except:
            escalas = None
    else:
        escalas = None
        data_consulta = date.today()
    return render(request,'globus/localizar_escala.html',{'escalas':escalas,'data_consulta':data_consulta})

@login_required
@permission_required('globus.view_settings')
def settings(request):
    if request.GET.get('empresa', None):
        try: # Carrega a empresa selecionada
            if request.user.is_superuser:
                empresa = Empresa.objects.get(id=request.GET.get('empresa', None))
            else:
                empresa = request.user.profile.empresas.filter(id=request.GET.get('empresa', None)).get()
        except:
            messages.error(request,'Empresa <b>não encontrada</b> ou <b>não habilitada</b>')
            return redirect('globus_settings')
        try: # Busca configuracao do app
            settings = Settings.objects.filter(empresa=empresa).get()
        except: # Caso ainda nao configurado, inicia com configuracao basica
            if Settings.objects.filter(empresa=empresa).count() == 0: # Trata possibilidade de entrada duplicada dos settings
                settings = Settings()
                settings.empresa = empresa
                settings.save()
                l = Log()
                l.modelo = "globus.settings"
                l.objeto_id = settings.id
                l.objeto_str = settings.empresa.nome
                l.usuario = request.user
                l.mensagem = "AUTO CREATED"
                l.save()
                messages.warning(request,'<b>Informativo:</b> Iniciado configurações para empresa')
            else:
                settings = None
                messages.error(request,'<b>Erro::</b> Identificado duplicatas nas configurações do sistema, entre em contato com o administrador.')
    else:
        settings = None
    form = SettingsForm(instance=settings)
    return render(request,'globus/settings.html',{'form':form,'settings':settings})

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
                l.objeto_id = registro.log_importacao
                l.objeto_str = registro.funcionario.matricula
                l.usuario = request.user
                l.mensagem = "CREATED"
                l.save()
                messages.success(request,f'Escala para <b>{registro.funcionario.matricula}</b> inserida')
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
        log_importacao = datetime.now()
        simular = True if request.POST['simular'] == 'True' else False
        if not request.POST['dados_validados'] in ['', '[]']:
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
                    escala.log_importacao = log_importacao
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
                if viagens_importadas > 0:
                    l = Log()
                    l.modelo = "globus.escala"
                    l.objeto_id = log_importacao
                    l.objeto_str = 'Importacao GLOBUS'
                    l.usuario = request.user
                    l.mensagem = "GLOBUS IMPORT"
                    l.save()
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
        l.objeto_id = registro.log_importacao
        l.objeto_str = registro.funcionario.matricula
        l.usuario = request.user
        l.mensagem = "UPDATE"
        l.save()
        messages.success(request,f'Escala funcionário <b>{registro.funcionario.matricula}</b> alterada')
        return redirect('globus_escala_id', id)
    else:
        return render(request,'globus/escala_id.html',{'form':form,'escala':escala})

@login_required
@permission_required('globus.change_settings')
def settings_update(request, id):
    try:
        settings = Settings.objects.get(pk=id)
        form = SettingsForm(request.POST, instance=settings)
        if form.is_valid():
            registro = form.save()
            l = Log()
            l.modelo = "globus.settings"
            l.objeto_id = registro.id
            l.objeto_str = registro.empresa.nome
            l.usuario = request.user
            l.mensagem = "UPDATE"
            l.save()
            messages.success(request,'Settings <b>escala</b> alterado')
            base_url = reverse('globus_settings')
            query_string =  urlencode({'empresa': registro.empresa.id})
            url = '{}?{}'.format(base_url, query_string)
            return redirect(url)
        else:
            return render(request,'globus/settings.html',{'form':form,'settings':settings})
    except Exception as e:
        messages.error(request,f'<b>Errro</b> ao alterar settings. <i>{e}</i>')
        return redirect('globus_settings', )
        
# METODOS DELETE
@login_required
@permission_required('globus.delete_escala')
def escala_delete(request, id):
    try:
        registro = Escala.objects.get(pk=id)
        l = Log()
        l.modelo = "globus.escala"
        l.objeto_id = registro.log_importacao
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