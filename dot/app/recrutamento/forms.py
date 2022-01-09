from django import forms
from .models import Candidato, Selecao, Vaga, Criterio
from pessoal.models import Cargo
from datetime import date

class SelecaoForm(forms.ModelForm):
    class Meta:
        model = Selecao
        fields = ['candidato','data','vaga','resultado','arquivar']
    data = forms.DateField(error_messages={'required': 'Informe uma data'},initial=date.today(),widget=forms.TextInput(attrs={'class':'form-control bg-light','type':'date','tabindex':'-1','placeholder':''}))
    vaga = forms.ModelChoiceField(error_messages={'required': 'Informe a vaga'}, queryset = Vaga.objects.filter(quantidade__gt=0), widget=forms.Select(attrs={'class':'form-select','placeholder':''}))
    resultado = forms.ChoiceField(required=False, choices=Selecao.RESULTADO_CHOICES, widget=forms.Select(attrs={'class':'form-control','placeholder':''}))
    arquivar = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch', 'tabindex':'-1'}))
    

class CandidatoForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = ['origem','nome','rg','cpf','sexo','vagas','data_nascimento','endereco','fone1','fone2','email','indicacao','pne','bloqueado_ate','detalhe','apresentacao','curriculo','mensagens','nova_mensagem','bloquear_mensagens']
    origem = forms.ChoiceField(required=False,choices=Candidato.ORIGEM_CHOICES, widget=forms.Select(attrs={'class':'form-select bg-light','tabindex':'-1'}))
    nome = forms.CharField(error_messages={'required': 'Informe o nome'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'','autofocus':'autofocus'}))
    rg = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    cpf = forms.CharField(error_messages={'required': 'Informe o CPF'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    sexo = forms.ChoiceField(required=False,choices=Candidato.SEXO_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))
    data_nascimento = forms.DateField(required=False, widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    endereco = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    bairro = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    cidade = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    uf = forms.CharField(required=False, max_length=2,widget=forms.TextInput(attrs={'class': 'form-control text-center','placeholder':''}))
    fone1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    fone2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','type':'email','placeholder':''}))
    indicacao = forms.CharField(required=False,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    pne = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch', 'tabindex':'-1'}))
    bloqueado_ate = forms.DateField(required=False, widget=forms.TextInput(attrs={'class':'form-control bg-light','type':'date'}))
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','style':'min-height:140px;','placeholder':''}))
    apresentacao = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control bg-light','placeholder':'','style':'min-height:140px;'}))
    curriculo = forms.FileField(required=False)
    mensagens = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':''}))
    bloquear_mensagens = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch', 'tabindex':'-1'}))


class VagaForm(forms.ModelForm):
    class Meta:
        model = Vaga
        fields = ['cargo','descricao','quantidade','visivel']
    cargo = forms.ModelChoiceField(error_messages={'required': 'Selecione um cargo'}, queryset = Cargo.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select','autofocus':'autofocus'}))
    descricao = forms.CharField(required=False,max_length=60,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    quantidade = forms.IntegerField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control bg-light','type':'number','min':'0','max':'999'}))

class CriterioForm(forms.ModelForm):
    class Meta:
        model = Criterio
        fields = ['nome']
    descricao = forms.CharField(error_messages={'required': 'Informe o nome do criterio'},max_length=50,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))