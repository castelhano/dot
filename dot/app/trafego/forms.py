from django import forms
from .models import Linha, Localidade, Trajeto, Evento, Providencia, Ocorrencia, Planejamento, Orgao, Agente, Enquadramento, Notificacao, Predefinido
from datetime import date, datetime


class LocalidadeForm(forms.ModelForm):
    class Meta:
        model = Localidade
        fields = ['nome','eh_garagem','troca_turno', 'ponto_de_controle']
    nome = forms.CharField(error_messages={'required': 'Defina um nome para localidade'},widget=forms.TextInput(attrs={'class': 'form-control','autofocus':'autofocus','placeholder':' '}))
    eh_garagem = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    troca_turno = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    ponto_de_controle = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class TrajetoForm(forms.ModelForm):
    class Meta:
        model = Trajeto
        fields = ['linha','sentido','seq','local','labels','fechado','detalhe']
    sentido = forms.ChoiceField(choices=Trajeto.SENTIDO_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))
    seq = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'1','max':'199', 'onfocus':'this.select();'}))
    fechado = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    detalhe = forms.CharField(required=False,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    

class LinhaForm(forms.ModelForm):
    class Meta:
        model = Linha
        fields = ['empresa','codigo','nome','classificacao','origem','destino','acesso_origem_km','acesso_destino_km','acesso_origem_minutos','acesso_destino_minutos','recolhe_origem_km','recolhe_destino_km','recolhe_origem_minutos','recolhe_destino_minutos','extensao_ida','extensao_volta','intervalo_ida','intervalo_volta', 'detalhe']
    codigo = forms.CharField(error_messages={'required': 'Campo Código OBRIGATÓRIO'},max_length=8,widget=forms.TextInput(attrs={'class': 'form-control bg-light fw-bold','placeholder':' '}))
    nome = forms.CharField(error_messages={'required': 'É necessário informar um noma para linha'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    classificacao = forms.ChoiceField(choices=Linha.CLASSIFICACAO_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))
    extensao_ida = forms.DecimalField(required=False,initial=0,min_value=0,max_digits=10,decimal_places=2,widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000','step':'.01', 'onfocus':'this.select();'}))
    extensao_volta = forms.DecimalField(required=False,initial=0,min_value=0,max_digits=10,decimal_places=2,widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000','step':'.01', 'onfocus':'this.select();'}))
    acesso_origem_km = forms.DecimalField(required=False,initial=0,min_value=0,max_digits=10,decimal_places=2,widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000','step':'.01', 'onfocus':'this.select();'}))
    acesso_destino_km = forms.DecimalField(required=False,initial=0,min_value=0,max_digits=10,decimal_places=2,widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000','step':'.01', 'onfocus':'this.select();'}))
    recolhe_origem_km = forms.DecimalField(required=False,initial=0,min_value=0,max_digits=10,decimal_places=2,widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000','step':'.01', 'onfocus':'this.select();'}))
    recolhe_destino_km = forms.DecimalField(required=False,initial=0,min_value=0,max_digits=10,decimal_places=2,widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000','step':'.01', 'onfocus':'this.select();'}))
    acesso_origem_minutos = forms.IntegerField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000', 'onfocus':'this.select();'}))
    acesso_destino_minutos = forms.IntegerField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000', 'onfocus':'this.select();'}))
    recolhe_origem_minutos = forms.IntegerField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000', 'onfocus':'this.select();'}))
    recolhe_destino_minutos = forms.IntegerField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000', 'onfocus':'this.select();'}))
    intervalo_ida = forms.IntegerField(required=False,initial=5, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'1','max':'60', 'onfocus':'this.select();'}))
    intervalo_volta = forms.IntegerField(required=False,initial=5, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'1','max':'60', 'onfocus':'this.select();'}))
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Detalhes', 'rows':4}))

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nome']
    nome = forms.CharField(error_messages={'required': 'Defina um nome para o evento'},widget=forms.TextInput(attrs={'class': 'form-control','autofocus':'autofocus','placeholder':' '}))

class ProvidenciaForm(forms.ModelForm):
    class Meta:
        model = Providencia
        fields = ['nome']
    nome = forms.CharField(error_messages={'required': 'Defina um nome para o evento'},widget=forms.TextInput(attrs={'class': 'form-control','autofocus':'autofocus','placeholder':' '}))

class OcorrenciaForm(forms.ModelForm):
    class Meta:
        model = Ocorrencia
        fields = ['empresa','evento','data','hora','linha','local','veiculo','condutor','indisciplina_condutor','gravidade','viagem_omitida','providencia','detalhe']
    evento = forms.ModelChoiceField(error_messages={'required': 'Selecione uma ocorrencia'}, queryset = Evento.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select bg-light fw-bold'}))
    data = forms.DateField(error_messages={'required': 'Informe a data da ocorrencia'},initial=date.today(),widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    hora = forms.TimeField(error_messages={'required': 'Informe a hora da ocorrencia'}, initial=datetime.now().strftime('%H:%M'), widget=forms.TextInput(attrs={'class':'form-control','type':'time'}))
    indisciplina_condutor = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    viagem_omitida = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    gravidade = forms.ChoiceField(choices=Ocorrencia.GRAVIDADE_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':' ','style':'min-height:350px;'}))
    providencia = forms.ModelChoiceField(required=False, queryset = Providencia.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select'}))

class PlanejamentoForm(forms.ModelForm):
    class Meta:
        model = Planejamento
        fields = ['empresa','linha','codigo','descricao','dia_tipo','patamares','ativo','pin']
    codigo = forms.CharField(error_messages={'required': 'Informe um código para o projeto', 'unique': 'Projeto com esse nome já existe'},max_length=8,widget=forms.TextInput(attrs={'class': 'form-control bg-light fw-bold','placeholder':' '}))
    descricao = forms.CharField(required=False, max_length=60,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    dia_tipo = forms.ChoiceField(choices=Planejamento.DIA_TIPO, widget=forms.Select(attrs={'class':'form-select'}))
    ativo = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    pin = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    def clean_codigo(self):
        return self.cleaned_data['codigo'].upper()

class OrgaoForm(forms.ModelForm):
    class Meta:
        model = Orgao
        fields = ['nome']
    nome = forms.CharField(error_messages={'required': 'Informe o nome do orgão'},widget=forms.TextInput(attrs={'class': 'form-control','autofocus':'autofocus','placeholder':' '}))

class AgenteForm(forms.ModelForm):
    class Meta:
        model = Agente
        fields = ['matricula','nome','orgao']
    
    matricula = forms.CharField(error_messages={'required': 'Informe a matricula do agente'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    nome = forms.CharField(error_messages={'required': 'Informe o nome do agente'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    orgao = forms.ModelChoiceField(error_messages={'required': 'Informe o nome do orgão'}, queryset = Orgao.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select bg-light', 'autofocus':'autofocus'}))

class EnquadramentoForm(forms.ModelForm):
    class Meta:
        model = Enquadramento
        fields = ['codigo','nome']
    codigo = forms.CharField(error_messages={'required': 'Informe o codigo do enquadramento'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ', 'autofocus':'autofocus'}))
    nome = forms.CharField(error_messages={'required': 'Informe o nome do orgão'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))

class PredefinidoForm(forms.ModelForm):
    class Meta:
        model = Predefinido
        fields = ['abbr','detalhe']
    abbr = forms.CharField(error_messages={'required': 'Informe a descricao abreviada'}, max_length=40, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ', 'autofocus':'autofocus'}))
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Detalhes', 'rows':4}))

class NotificacaoForm(forms.ModelForm):
    class Meta:
        model = Notificacao
        fields = ['empresa','tipo','codigo','data','hora','veiculo','linha','funcionario','agente','enquadramento','local','valor','prazo','detalhe','tratativa','veiculo_lacrado']
    tipo = forms.ChoiceField(choices=Notificacao.TIPO_CHOICES, widget=forms.Select(attrs={'class':'form-select bg-light fw-bold'}))
    codigo = forms.CharField(error_messages={'required': 'Informe o cod da notificação'}, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    data = forms.DateField(error_messages={'required': 'Informe a data da notificação'}, initial=date.today(),widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    hora = forms.TimeField(required=False, initial=datetime.now().strftime('%H:%M'), widget=forms.TextInput(attrs={'class':'form-control','type':'time'}))
    valor = forms.DecimalField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control','onfocus':'this.select();'}))
    prazo = forms.DateField(required=False,widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    detalhe = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    tratativa = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','style':'min-height:305px;','placeholder':'Tratativas'}))
    veiculo_lacrado = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))