from django import forms
from .models import Veiculo, Area, Vaga, Visitante, RegistroFuncionario, RegistroVisitante
# from django.contrib.auth.models import User
from datetime import datetime, date, timedelta


class VeiculoForm(forms.ModelForm):
    class Meta:
        model = Veiculo
        fields = ['modelo','cor','placa','funcionario','valido_ate','km_inicial']
    modelo = forms.CharField(error_messages={'required': 'Informe o modelo'},max_length=20,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    cor = forms.CharField(required=False,max_length=15, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    placa = forms.CharField(error_messages={'required': 'Informe a placa do veiculo','unique':'Placa já cadastrada para outro veiculo'}, widget=forms.TextInput(attrs={'class':'form-control text-uppercase','placeholder':' '}))
    valido_ate = forms.DateField(required=False, initial=date.today() + timedelta(days=30), widget=forms.TextInput(attrs={'class':'form-control bg-body-secondary','type':'date'}))
    km_inicial = forms.IntegerField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'9999999','onfocus':'this.select()'}))
    def clean_placa(self):
        return self.cleaned_data['placa'].upper()

class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ['nome','css_breakpoint']
    nome = forms.CharField(error_messages={'required': 'Informe um nome para area'}, max_length=15, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus'}))
    css_breakpoint = forms.CharField(required=False, initial='col-lg', max_length=200, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))

class VagaForm(forms.ModelForm):
    class Meta:
        model = Vaga
        fields = ['codigo','area','fixa','inativa','detalhe']
    area = forms.ModelChoiceField(error_messages={'required': 'Área inválida'}, empty_label=None, queryset = Area.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select','autofocus':'autofocus'}))
    codigo = forms.CharField(error_messages={'required': 'Informe o código da vaga'}, max_length=4, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    fixa = forms.BooleanField(required=False,initial=False,widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    inativa = forms.BooleanField(required=False,initial=False,widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    detalhe = forms.CharField(required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))

class VisitanteForm(forms.ModelForm):
    class Meta:
        model = Visitante
        fields = ['nome','empresa','rg','cpf','fone1','fone2','email','endereco','bairro','cidade','uf','foto','detalhe','bloqueado']
    nome = forms.CharField(error_messages={'required': 'Informe o nome do visitante'}, max_length=120,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus'}))
    empresa = forms.CharField(required=False, max_length=30,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    rg = forms.CharField(required=False, max_length=15, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    cpf = forms.CharField(error_messages={'required': 'Informe o cpf do visitante', 'unique':'CPF já cadastrado'}, max_length=15,widget=forms.TextInput(attrs={'class': 'form-control bg-body-secondary','placeholder':' '}))
    fone1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    fone2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    endereco = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    bairro = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    cidade = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    uf = forms.CharField(required=False, max_length=2,widget=forms.TextInput(attrs={'class': 'form-control text-center','placeholder':' '}))
    foto = forms.ImageField(required=False)
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','style':'min-height:200px;','placeholder':'Detalhes'}))
    bloqueado = forms.BooleanField(required=False,initial=False,widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class EntradaFuncionarioForm(forms.ModelForm):
    class Meta:
        model = RegistroFuncionario
        fields = ['vaga','veiculo','data_entrada','hora_entrada','km_entrada','detalhe']
    data_entrada = forms.DateField(error_messages={'required': 'Informe a data de entrada'}, initial=date.today(), widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    hora_entrada = forms.TimeField(error_messages={'required': 'Informe a hora de entrada'}, initial=datetime.now().strftime('%H:%M'),widget=forms.TextInput(attrs={'class':'form-control','type':'time'}))
    km_entrada = forms.IntegerField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'9999999','onfocus':'this.select()'}))
    detalhe = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))

class SaidaFuncionarioForm(forms.ModelForm):
    class Meta:
        model = RegistroFuncionario
        fields = ['data_saida','hora_saida','km_saida']
    data_saida = forms.DateField(required=False, widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    hora_saida = forms.TimeField(required=False, widget=forms.TextInput(attrs={'class':'form-control','type':'time'}))
    km_saida = forms.IntegerField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'9999999','onfocus':'this.select()'}))

class EntradaVisitanteForm(forms.ModelForm):
    class Meta:
        model = RegistroVisitante
        fields = ['vaga','visitante','modelo','cor','placa','autorizado_por','data_entrada','hora_entrada','km_entrada','detalhe']
    modelo = forms.CharField(required=False, max_length=20,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    cor = forms.CharField(required=False, max_length=15,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    placa = forms.CharField(required=False, max_length=15,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    autorizado_por = forms.CharField(required=False, max_length=40,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    data_entrada = forms.DateField(error_messages={'required': 'Informe a data de entrada'}, initial=date.today(), widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    hora_entrada = forms.TimeField(error_messages={'required': 'Informe a hora de entrada'}, widget=forms.TextInput(attrs={'class':'form-control','type':'time'}))
    km_entrada = forms.IntegerField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'9999999','onfocus':'this.select()'}))
    detalhe = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))

class SaidaVisitanteForm(forms.ModelForm):
    class Meta:
        model = RegistroVisitante
        fields = ['data_saida','hora_saida','km_saida']
    data_saida = forms.DateField(required=False, widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    hora_saida = forms.TimeField(required=False, widget=forms.TextInput(attrs={'class':'form-control','type':'time'}))
    km_saida = forms.IntegerField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'9999999','onfocus':'this.select()'}))