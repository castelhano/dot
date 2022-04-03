from django import forms
from .models import Indicador, Apontamento, Staff, Diretriz, Label, Analise, Plano
from datetime import date
from django.contrib.auth.models import User


class IndicadorForm(forms.ModelForm):
    class Meta:
        model = Indicador
        fields = ['nome','meta','quanto_maior_melhor','ativo']
    nome = forms.CharField(error_messages={'required': 'Informe o nome do indicador','unique': 'Já existe indicador com este nome'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'','autofocus':'autofocus'}))
    meta = forms.DecimalField(required=False,initial=0,widget=forms.TextInput(attrs={'class': 'form-control','onfocus':'this.select();'}))
    quanto_maior_melhor = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    ativo = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class ApontamentoForm(forms.ModelForm):
    class Meta:
        model = Apontamento
        fields = ['indicador','referencia','valor','meta']
    indicador = forms.ModelChoiceField(error_messages={'required': 'Selecione o indicador'}, queryset = Indicador.objects.filter(ativo=True).order_by('nome'), widget=forms.Select(attrs={'class':'form-select','autofocus':'autofocus'}))
    valor = forms.DecimalField(required=False,initial=0,widget=forms.TextInput(attrs={'class': 'form-control','onfocus':'this.select();'}))
    meta = forms.DecimalField(required=False,initial=0,widget=forms.TextInput(attrs={'class': 'form-control','onfocus':'this.select();'}))

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['usuario','role']
    usuario = forms.ModelChoiceField(error_messages={'required': 'Selecione o usuario','unique': 'Usuário já está no staff'}, queryset = User.objects.filter(is_active=True, is_staff=True).order_by('username'), widget=forms.Select(attrs={'class':'form-select','autofocus':'autofocus'}))
    role = forms.ChoiceField(error_messages={'required': 'Selecione um perfil'}, choices=Staff.ROLE_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))
    

class DiretrizForm(forms.ModelForm):
    class Meta:
        model = Diretriz
        fields = ['indicador','titulo','detalhe']
    indicador = forms.ModelChoiceField(error_messages={'required': 'Selecione o indicador'}, queryset = Indicador.objects.filter(ativo=True).order_by('nome'), widget=forms.Select(attrs={'class':'form-select','autofocus':'autofocus'}))
    titulo = forms.CharField(error_messages={'required': 'Informe o titulo'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Detalhamento', 'style':'min-height:300px'}))

class LabelForm(forms.ModelForm):
    class Meta:
        model = Label
        fields = ['nome','cor','fonte']
    nome = forms.CharField(error_messages={'required': 'Informe o nome da label'}, max_length=15, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'','autofocus':'autofocus','onkeyup':'labelPreview()'}))
    cor = forms.CharField(required=False, initial='#F1F1F1', widget=forms.TextInput(attrs={'class': 'form-control','type':'color','onchange':'labelPreview()'}))
    fonte = forms.CharField(required=False, initial='#000', widget=forms.TextInput(attrs={'class': 'form-control','type':'color','onchange':'labelPreview()'}))

class AnaliseForm(forms.ModelForm):
    class Meta:
        model = Analise
        fields = ['indicador','descricao','critico','concluido']
    indicador = forms.ModelChoiceField(error_messages={'required': 'Selecione o indicador'}, queryset = Indicador.objects.filter(ativo=True).order_by('nome'), widget=forms.Select(attrs={'class':'form-select','autofocus':'autofocus'}))
    descricao = forms.CharField(error_messages={'required': 'É necessário informar algo na descrição'}, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Detalhamento', 'style':'min-height:300px'}))
    critico = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    concluido = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class PlanoForm(forms.ModelForm):
    class Meta:
        model = Plano
        fields = ['diretriz','analise','titulo','detalhe','inicio','termino','responsavel','staff','status']
    diretriz = forms.ModelChoiceField(error_messages={'required': 'Selecione o diretriz'}, queryset = Diretriz.objects.filter(ativo=True).order_by('id'), widget=forms.Select(attrs={'class':'form-select','autofocus':'autofocus'}))
    analise = forms.ModelChoiceField(required=False, queryset = Analise.objects.filter(concluido=False).order_by('id'), widget=forms.Select(attrs={'class':'form-select'}))
    titulo = forms.CharField(error_messages={'required': 'Informe o titulo'}, max_length=80, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Detalhamento', 'style':'min-height:300px'}))
    inicio = forms.DateField(required=False, initial=date.today(), widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    termino = forms.DateField(required=False, widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    responsavel = forms.ModelChoiceField(required=False, queryset = User.objects.filter(is_active=True, is_staff=True).order_by('username'), widget=forms.Select(attrs={'class':'form-select'}))
    status = forms.ChoiceField(error_messages={'required': 'Selecione o status'}, initial='E', choices=Plano.STATUS_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))