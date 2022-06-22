from django import forms
from .models import Indicador, Apontamento, Staff, Diretriz, Label, Analise, Plano, Settings
from datetime import date
from django.contrib.auth.models import User


class IndicadorForm(forms.ModelForm):
    class Meta:
        model = Indicador
        fields = ['nome','meta','medida','precisao','quanto_maior_melhor','ativo']
    nome = forms.CharField(error_messages={'required': 'Informe o nome do indicador','unique': 'Já existe indicador com este nome'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus'}))
    meta = forms.DecimalField(required=False,initial=0,widget=forms.TextInput(attrs={'class': 'form-control','onfocus':'this.select();'}))
    medida = forms.CharField(required=False, max_length=6, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    precisao = forms.CharField(error_messages={'required': 'Informe a precisão do indicador'}, initial=2, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':0,'max':4,'step':1,'placeholder':' '}))
    quanto_maior_melhor = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    ativo = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    percentual = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class ApontamentoForm(forms.ModelForm):
    class Meta:
        model = Apontamento
        fields = ['empresa','indicador','valor']
    valor = forms.DecimalField(required=False,initial=0,widget=forms.TextInput(attrs={'class': 'form-control','onfocus':'this.select();'}))

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['usuario','role']
    usuario = forms.ModelChoiceField(error_messages={'required': 'Selecione o usuario','unique': 'Usuário já está no staff'}, queryset = User.objects.filter(is_active=True, is_staff=True).order_by('username'), widget=forms.Select(attrs={'class':'form-select','autofocus':'autofocus'}))
    role = forms.ChoiceField(error_messages={'required': 'Selecione um perfil'}, choices=Staff.ROLE_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))
    

class DiretrizForm(forms.ModelForm):
    class Meta:
        model = Diretriz
        fields = ['empresa','indicador','analise','titulo','detalhe']
    titulo = forms.CharField(error_messages={'required': 'Informe o titulo'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    indicador = forms.ModelChoiceField(error_messages={'required': 'Selecione o indicador'}, queryset = Indicador.objects.filter(ativo=True).order_by('nome'), widget=forms.Select(attrs={'class':'form-select'}))
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Detalhamento', 'style':'min-height:300px'}))
    analise = forms.ModelChoiceField(required=False, queryset = Analise.objects.filter(tipo__in=['N','M']))

class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['nome','cor','fonte']
    nome = forms.CharField(error_messages={'required': 'Informe o nome da label'}, max_length=15, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus','onkeyup':'labelPreview()'}))
    cor = forms.CharField(required=False, initial='#F1F1F1', widget=forms.TextInput(attrs={'class': 'form-control','type':'color','onchange':'labelPreview()'}))
    fonte = forms.CharField(required=False, initial='#000', widget=forms.TextInput(attrs={'class': 'form-control','type':'color','onchange':'labelPreview()'}))

class PlanoForm(forms.ModelForm):
    class Meta:
        model = Plano
        fields = ['diretriz','analise','titulo','detalhe','inicio','termino','responsavel','staff','labels']
    titulo = forms.CharField(error_messages={'required': 'Informe o titulo'}, max_length=80, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus'}))
    diretriz = forms.ModelChoiceField(error_messages={'required': 'Selecione o diretriz'}, queryset = Diretriz.objects.filter(ativo=True))
    analise = forms.ModelChoiceField(required=False, queryset = Analise.objects.filter(concluido=False))
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Detalhamento', 'style':'min-height:300px'}))
    inicio = forms.DateField(required=False, initial=date.today(), widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    termino = forms.DateField(required=False, widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    responsavel = forms.ModelChoiceField(required=False, queryset = Staff.objects.filter(usuario__is_active=True, usuario__is_staff=True))
    labels = forms.ModelMultipleChoiceField(required=False, queryset = Label.objects.all(), widget=forms.widgets.SelectMultiple(attrs={'class':'d-none'}))

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['analytics_foco_mes_atual']
    analytics_foco_mes_atual = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))