from django import forms
from .models import Grupo, Container, Ativo, File, Limite
from pessoal.models import Setor
from core.models import Empresa
from datetime import date



class GrupoForm(forms.ModelForm):
    class Meta:
        model = Grupo
        fields = ['nome','tempo_guarda']
    nome = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus'}))
    tempo_guarda = forms.IntegerField(initial=12, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'9999','onfocus':'this.select()'}))

class ContainerForm(forms.ModelForm):
    class Meta:
        model = Container
        fields = ['nome','capacidade','inativo']
    nome = forms.CharField(max_length=30,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus'}))
    capacidade = forms.IntegerField(initial=10, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'1','max':'9999', 'onfocus':'this.select()'}))
    inativo = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch', 'tabindex':'-1'}))

class AtivoForm(forms.ModelForm):
    class Meta:
        model = Ativo
        fields = ['empresa','setor','grupo','responsavel','chaves','fisico','container']
    entrada = forms.DateField(error_messages={'required': 'Data inválida'}, initial=date.today(), widget=forms.TextInput(attrs={'class':'form-control','type':'date','readonly':'','tabindex':'-1'}))
    setor = forms.ModelChoiceField(required=False, queryset = Setor.objects.all().order_by('nome'), empty_label=None, widget=forms.Select(attrs={'class':'form-select'}))
    grupo = forms.ModelChoiceField(error_messages={'required': 'Selecione um grupo'}, queryset = Grupo.objects.all().order_by('nome'), empty_label=None, widget=forms.Select(attrs={'class':'form-select'}))
    container = forms.ModelChoiceField(required=False, queryset = Container.objects.filter(inativo=False).order_by('nome'), widget=forms.Select(attrs={'class':'form-select'}))
    responsavel = forms.CharField(max_length=40,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    fisico = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    chaves = forms.CharField(required=False, max_length=120, widget=forms.TextInput(attrs={'class': 'form-control tagin','placeholder':' '}))


class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['ativo','file']
    file = forms.FileField(required=True, widget=forms.ClearableFileInput(attrs={'class': 'form-control','accept':'.pdf,.doc,.docx,.odt,.png,.jpg,.xls,.xlsx,.mp4'}))


class LimiteForm(forms.ModelForm):
    class Meta:
        model = Limite
        fields = ['empresa','quantidade']
    empresa = forms.ModelChoiceField(error_messages={'required': 'Empresa inválida', 'unique':'Já existe limite definido para esta empresa'}, queryset = Empresa.objects.all())
    quantidade = forms.IntegerField(required=False, initial=100, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'99999','onfocus':'this.select()'}))