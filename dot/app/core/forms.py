from django import forms
from .models import Empresa
from django.contrib.auth.models import User

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nome','cnpj','razao_social','inscricao_estadual','inscricao_municipal','cnae','atividade','endereco','bairro','cidade','uf','cep','fone','fax']
    nome = forms.CharField(error_messages={'required': 'Nome requerido'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'','autofocus':'autofocus'}))
    cnpj = forms.CharField(required=False, max_length=18 ,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    razao_social = forms.CharField(required=False, max_length=80,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    inscricao_estadual = forms.CharField(required=False, max_length=15,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    inscricao_municipal = forms.CharField(required=False, max_length=15,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    cnae = forms.CharField(required=False, max_length=10,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    atividade = forms.CharField(required=False, max_length=150,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    endereco = forms.CharField(required=False, max_length=150,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    bairro = forms.CharField(required=False, max_length=50,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    cidade = forms.CharField(required=False, max_length=50,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    uf = forms.CharField(required=False, max_length=2,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    cep = forms.CharField(required=False, max_length=10,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','is_superuser','is_staff','is_active']
    username = forms.CharField(error_messages={'required': 'Username requerido'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'','autofocus':'autofocus'}))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'','type':'email'}))
    is_superuser = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    is_staff = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    is_active = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    