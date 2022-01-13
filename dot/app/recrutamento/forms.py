from django import forms
from .models import Candidato, Selecao, Vaga, Criterio
from pessoal.models import Cargo
from django.core.exceptions import ValidationError
from pessoal.validators import cpf_valid
from datetime import date, datetime

class SelecaoForm(forms.ModelForm):
    class Meta:
        model = Selecao
        fields = ['candidato','data','hora','vaga','arquivar']
    data = forms.DateField(error_messages={'required': 'Informe uma data'},initial=date.today(),widget=forms.TextInput(attrs={'class':'form-control','type':'date','placeholder':''}))
    hora = forms.TimeField(required=False, initial=datetime.now().strftime('%H:%M'), widget=forms.TextInput(attrs={'class':'form-control','type':'time', 'placeholder':''}))
    vaga = forms.ModelChoiceField(error_messages={'required': 'Informe a vaga'}, queryset = Vaga.objects.filter(quantidade__gt=0), widget=forms.Select(attrs={'class':'form-select','placeholder':'','autofocus':'autofocus'}))
    arquivar = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch', 'tabindex':'-1'}))
    

class CandidatoForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = ['nome','rg','cpf','sexo','vagas','data_nascimento','endereco','bairro','cidade','uf','fone1','fone2','email','indicacao','pne','bloqueado_ate','detalhe','curriculo','bloquear_mensagens']
    origem = forms.ChoiceField(required=False,choices=Candidato.ORIGEM_CHOICES, widget=forms.Select(attrs={'class':'form-select bg-light','tabindex':'-1'}))
    nome = forms.CharField(error_messages={'required': 'Informe o nome'},widget=forms.TextInput(attrs={'class': 'form-control bg-light','placeholder':'','autofocus':'autofocus'}))
    vagas = forms.CharField(error_messages={'required': 'Necessário informar pelo menos uma vaga'})
    rg = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    cpf = forms.CharField(error_messages={'required': 'Informe o CPF', 'unique': 'CPF já cadastrado'},widget=forms.TextInput(attrs={'class': 'form-control bg-light','placeholder':''}))
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
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Detalhes'}))
    apresentacao = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Apresentação'}))
    curriculo = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control','accept':'.pdf,.doc,.docx,.odt'}))
    mensagens = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Mensagens'}))
    bloquear_mensagens = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch', 'tabindex':'-1'}))
    def clean(self):
        cleaned_data = super(CandidatoForm, self).clean()
        if not cpf_valid(cleaned_data.get('cpf')):
            raise ValidationError("O CPF digitado <b>não é válido</b>")

class VagaForm(forms.ModelForm):
    class Meta:
        model = Vaga
        fields = ['cargo','descricao','quantidade','visivel']
    cargo = forms.ModelChoiceField(error_messages={'required': 'Selecione um cargo'}, queryset = Cargo.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select','autofocus':'autofocus'}))
    descricao = forms.CharField(required=False,max_length=60,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    quantidade = forms.IntegerField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control bg-light','type':'number','min':'0','max':'999', 'onfocus':'this.select();'}))
    visivel = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))

class CriterioForm(forms.ModelForm):
    class Meta:
        model = Criterio
        fields = ['nome']
    nome = forms.CharField(error_messages={'required': 'Informe o nome do criterio'},max_length=50,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':'', 'autofocus':'autofocus'}))