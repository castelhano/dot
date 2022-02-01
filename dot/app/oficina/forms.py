from django import forms
from .models import Frota, Marca, Categoria, Componente, Modelo, Classificacao, Carroceria
from datetime import date


class MarcaForm(forms.ModelForm):
    class Meta:
        model = Marca
        fields = ['nome']
    nome = forms.CharField(error_messages={'required': 'Informe um nome para marca'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'','autofocus':'autofocus'}))

class ClassificacaoForm(forms.ModelForm):
    class Meta:
        model = Classificacao
        fields = ['nome']
    nome = forms.CharField(error_messages={'required': 'Informe um nome para classificação'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'','autofocus':'autofocus'}))

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome']
    nome = forms.CharField(error_messages={'required': 'Informe um nome para categoria'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'','autofocus':'autofocus'}))

class ComponenteForm(forms.ModelForm):
    class Meta:
        model = Componente
        fields = ['nome']
    nome = forms.CharField(error_messages={'required': 'Informe um nome para o componente'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'','autofocus':'autofocus'}))

class CarroceriaForm(forms.ModelForm):
    class Meta:
        model = Carroceria
        fields = ['nome']
    nome = forms.CharField(error_messages={'required': 'Informe um nome para a carroceria'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'','autofocus':'autofocus'}))

class ModeloForm(forms.ModelForm):
    class Meta:
        model = Modelo
        fields = ['marca','nome']
    marca = forms.ModelChoiceField(error_messages={'required': 'Selecione uma marca'},queryset = Marca.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select','autofocus':'autofocus'}))
    nome = forms.CharField(error_messages={'required': 'Informe um nome para o modelo'},widget=forms.TextInput(attrs={'class':'form-control','placeholder':''}))

class FrotaForm(forms.ModelForm):
    class Meta:
        model = Frota
        fields = ['empresa','prefixo','placa','renavan','chassi','modelo','capacidade_tanque','catraca_inicial','media_ideal','categoria','carroceria','classificacao','ano_fabricacao','ano_modelo','aniversario','inicio_operacao','km_inicial','componentes','detalhe']
    prefixo = forms.CharField(error_messages={'required': 'É necessário informar um prefixo para o veiculo'},widget=forms.TextInput(attrs={'class':'form-control bg-light fw-bold','placeholder':''}))
    placa = forms.CharField(required=False,widget=forms.TextInput(attrs={'class':'form-control','placeholder':''}))
    renavan = forms.CharField(required=False, max_length=11, widget=forms.TextInput(attrs={'class':'form-control','placeholder':''}))
    chassi = forms.CharField(required=False, max_length=17, widget=forms.TextInput(attrs={'class':'form-control','placeholder':''}))
    capacidade_tanque = forms.IntegerField(required=False, initial=0,widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000','onfocus':'this.select();'}))
    catraca_inicial = forms.IntegerField(required=False, initial=0,widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'99999999','onfocus':'this.select();'}))
    media_ideal = forms.CharField(required=False,initial=0,widget=forms.TextInput(attrs={'class':'form-control','type':'number','min':0,'max':30,'step':'0.01','placeholder':'','onfocus':'this.select();'}))
    categoria = forms.ModelChoiceField(required=False, queryset = Categoria.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select'}))
    carroceria = forms.ModelChoiceField(required=False, queryset = Carroceria.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select'}))
    classificacao = forms.ModelChoiceField(required=False, queryset = Classificacao.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select'}))
    componentes = forms.ModelMultipleChoiceField(required=False, queryset = Componente.objects.all().order_by('nome'), widget=forms.widgets.SelectMultiple(attrs={'class':'form-select','style':'min-height:200px'}))
    ano_fabricacao = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'1980','max':'2100'}))
    ano_modelo = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'1980','max':'2100'}))
    inicio_operacao = forms.DateField(required=False,initial=date.today(),widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    aniversario = forms.DateField(required=False,widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    km_inicial = forms.CharField(required=False,initial=0,widget=forms.TextInput(attrs={'class':'form-control','placeholder':'','onfocus':'this.select();'}))
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Detalhes', 'style':'min-height:300px'}))