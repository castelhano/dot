from django import forms
from .models import Classificacao, Reclamacao, Settings
from datetime import date, datetime


class ClassificacaoForm(forms.ModelForm):
    class Meta:
        model = Classificacao
        fields = ['nome','tipo']
    nome = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus'}))
    tipo = forms.ChoiceField(error_messages={'required': 'Escolha um <b>tipo</b> para reclamacao'}, choices=Classificacao.TIPO_CHOICES, widget=forms.Select(attrs={'class':'form-select bg-light'}))


class ReclamacaoForm(forms.ModelForm):
    class Meta:
        model = Reclamacao
        fields = ['empresa','origem','data','hora','classificacao','veiculo','linha','funcionario','detalhe','parecer','reclamante','fone1','fone2','email','tratado','retorno']
    data = forms.DateField(initial=date.today(), widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    hora = forms.TimeField(required=False, initial=datetime.now().strftime('%H:%M'), widget=forms.TextInput(attrs={'class':'form-control','type':'time'}))
    classificacao = forms.ModelChoiceField(required=False, queryset = Classificacao.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select bg-light'}))
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Detalhes','style':'min-height:200px;'}))
    parecer = forms.ChoiceField(required=False,choices=Reclamacao.PARECER_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))
    reclamante = forms.CharField(required=False,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    fone1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    fone2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ', 'type':'email'}))
    tratado = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch', 'tabindex':'-1'}))
    retorno = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Retorno','style':'min-height:150px;'}))

class SiteForm(forms.ModelForm):
    class Meta:
        model = Reclamacao
        fields = ['data','hora','classificacao','veiculo','linha','detalhe','reclamante','fone1','fone2','email']

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['prazo_resposta']
    prazo_resposta = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'bg-light form-control','type':'number','min':'1','max':'90','autofocus':'autofocus'}))