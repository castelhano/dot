from django import forms
from .models import Candidato, Selecao, Vaga, Criterio, Settings
from pessoal.models import Cargo
from django.core.exceptions import ValidationError
from pessoal.validators import cpf_valid
from datetime import date, datetime, timedelta

class SelecaoForm(forms.ModelForm):
    class Meta:
        model = Selecao
        fields = ['candidato','data','hora','vaga','arquivar','detalhes']
    data = forms.DateField(error_messages={'required': 'Informe uma data'},initial=date.today() + timedelta(1),widget=forms.TextInput(attrs={'class':'form-control','type':'date','placeholder':' '}))
    hora = forms.TimeField(required=False, initial='08:00', widget=forms.TextInput(attrs={'class':'form-control','type':'time', 'placeholder':''}))
    arquivar = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch', 'tabindex':'-1'}))
    detalhes = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Detalhes', 'data-i18n':'common.details', 'data-i18n-target':'placeholder'}))
    

class CandidatoForm(forms.ModelForm):
    class Meta:
        model = Candidato
        fields = ['nome','rg','cpf','sexo','vagas','data_nascimento','endereco','bairro','cidade','uf','fone1','fone2','email','indicacao','pne','bloqueado_ate','detalhe','curriculo']
    origem = forms.ChoiceField(required=False,choices=Candidato.ORIGEM_CHOICES, widget=forms.Select(attrs={'class':'form-select','tabindex':'-1'}))
    nome = forms.CharField(error_messages={'required': 'Informe o nome'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus'}))
    rg = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    cpf = forms.CharField(error_messages={'required': 'Informe o CPF', 'unique': 'CPF já cadastrado'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    sexo = forms.ChoiceField(required=False,choices=Candidato.SEXO_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))
    data_nascimento = forms.DateField(required=False, widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    endereco = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    bairro = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    cidade = forms.CharField(required=False, initial='Cuiabá', widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    uf = forms.CharField(required=False, max_length=2, initial='MT', widget=forms.TextInput(attrs={'class': 'form-control text-center','placeholder':' '}))
    fone1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    fone2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','type':'email','placeholder':' '}))
    indicacao = forms.CharField(required=False,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    pne = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch', 'tabindex':'-1'}))
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Detalhes'}))
    bloqueado_ate = forms.DateField(required=False, widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    apresentacao = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Apresentação', 'data-i18n':'common.presentation', 'data-i18n-target':'placeholder'}))
    curriculo = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control','accept':'.pdf,.doc,.docx,.odt'}))
    def clean(self):
        cleaned_data = super(CandidatoForm, self).clean()
        if not cpf_valid(cleaned_data.get('cpf')):
            raise ValidationError("O CPF digitado <b>não é válido</b>")

class VagaForm(forms.ModelForm):
    class Meta:
        model = Vaga
        fields = ['cargo','descricao','quantidade','visivel']
    cargo = forms.ModelChoiceField(error_messages={'required': 'Selecione um cargo'}, queryset = Cargo.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select','autofocus':'autofocus'}))
    descricao = forms.CharField(required=False,max_length=60,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    quantidade = forms.IntegerField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'999', 'onfocus':'this.select();'}))
    visivel = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))

class CriterioForm(forms.ModelForm):
    class Meta:
        model = Criterio
        fields = ['nome']
    nome = forms.CharField(error_messages={'required': 'Informe o nome do criterio'},max_length=50,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ', 'autofocus':'autofocus'}))

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['redirecinar_cadastro_ao_aprovar','exibir_quantidade_vagas_site','abater_saldo_vagas_ao_aprovar','descartar_reprovados', 'dias_bloqueio']
    redirecinar_cadastro_ao_aprovar = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    exibir_quantidade_vagas_site = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    abater_saldo_vagas_ao_aprovar = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    descartar_reprovados = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    dias_bloqueio = forms.IntegerField(required=False,initial=90, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'999', 'onfocus':'this.select();'}))