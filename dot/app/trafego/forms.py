from django import forms
from .models import Linha, Localidade, Evento, Providencia, Ocorrencia
from datetime import date, datetime


class LocalidadeForm(forms.ModelForm):
    class Meta:
        model = Localidade
        fields = ['nome','eh_garagem','troca_turno', 'ponto_de_controle']
    nome = forms.CharField(error_messages={'required': 'Defina um nome para localidade'},widget=forms.TextInput(attrs={'class': 'form-control','autofocus':'autofocus','placeholder':''}))
    eh_garagem = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    troca_turno = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    ponto_de_controle = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class LinhaForm(forms.ModelForm):
    class Meta:
        model = Linha
        fields = ['empresa','codigo','nome','classificacao','origem','destino','acesso_origem_km','acesso_destino_km','acesso_origem_minutos','acesso_destino_minutos','recolhe_origem_km','recolhe_destino_km','recolhe_origem_minutos','recolhe_destino_minutos','extensao_ida','extensao_volta','intervalo_ida','intervalo_volta', 'detalhe']
    codigo = forms.CharField(error_messages={'required': 'Campo Código OBRIGATÓRIO'},max_length=8,widget=forms.TextInput(attrs={'class': 'form-control bg-light fw-bold','placeholder':''}))
    nome = forms.CharField(error_messages={'required': 'É necessário informar um noma para linha'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    classificacao = forms.ChoiceField(choices=Linha.CLASSIFICACAO_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))
    origem = forms.ModelChoiceField(required=False, queryset = Localidade.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select'}))
    destino = forms.ModelChoiceField(required=False, queryset = Localidade.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select'}))
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
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Detalhes', 'rows':4,'tabindex':'-1'}))

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nome']
    nome = forms.CharField(error_messages={'required': 'Defina um nome para o evento'},widget=forms.TextInput(attrs={'class': 'form-control','autofocus':'autofocus','placeholder':''}))

class ProvidenciaForm(forms.ModelForm):
    class Meta:
        model = Providencia
        fields = ['nome']
    nome = forms.CharField(error_messages={'required': 'Defina um nome para o evento'},widget=forms.TextInput(attrs={'class': 'form-control','autofocus':'autofocus','placeholder':''}))

class OcorrenciaForm(forms.ModelForm):
    class Meta:
        model = Ocorrencia
        fields = ['empresa','evento','data','hora','linha','local','veiculo','condutor','indisciplina_condutor','gravidade','viagem_omitida','providencia','detalhe']
    evento = forms.ModelChoiceField(error_messages={'required': 'Selecione uma ocorrencia'}, queryset = Evento.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select bg-light fw-bold'}))
    data = forms.DateField(error_messages={'required': 'Informe a data da ocorrencia'},initial=date.today(),widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    hora = forms.TimeField(error_messages={'required': 'Informe a hora da ocorrencia'}, initial=datetime.now().strftime('%H:%M'), widget=forms.TextInput(attrs={'class':'form-control','type':'time'}))
    local = forms.ModelChoiceField(required=False, queryset = Localidade.objects.filter(ponto_de_controle=True).order_by('nome'), widget=forms.Select(attrs={'class':'form-select'}))
    indisciplina_condutor = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    viagem_omitida = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    gravidade = forms.ChoiceField(choices=Ocorrencia.GRAVIDADE_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'','style':'min-height:350px;'}))
    providencia = forms.ModelChoiceField(required=False, queryset = Providencia.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select'}))