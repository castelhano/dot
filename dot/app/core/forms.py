from django import forms
from .models import Empresa, Agenda, Feriado, Issue, Settings
from datetime import date
from django.contrib.auth.models import User, Group

class EmpresaForm(forms.ModelForm):
    class Meta:
        model = Empresa
        fields = ['nome','cnpj','razao_social','inscricao_estadual','inscricao_municipal','cnae','atividade','endereco','bairro','cidade','uf','cep','fone','fax','logo','footer']
    nome = forms.CharField(error_messages={'required': 'Nome requerido'},max_length=20, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus'}))
    cnpj = forms.CharField(required=False, max_length=18 ,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    razao_social = forms.CharField(required=False, max_length=80,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    inscricao_estadual = forms.CharField(required=False, max_length=15,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    inscricao_municipal = forms.CharField(required=False, max_length=15,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    cnae = forms.CharField(required=False, max_length=10,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    atividade = forms.CharField(required=False, max_length=150,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    endereco = forms.CharField(required=False, max_length=150,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    bairro = forms.CharField(required=False, max_length=50,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    cidade = forms.CharField(required=False, max_length=50,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    uf = forms.CharField(required=False, max_length=2,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    cep = forms.CharField(required=False, max_length=10,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    fone = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    fax = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    logo = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control','accept':'image/*'}))
    footer = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','style':'min-height:200px;','placeholder':'Rodapé padrão MD Report'}))

class AgendaForm(forms.ModelForm):
    class Meta:
        model = Agenda
        fields = ['data','inicio','termino','titulo','detalhe','participantes','local','tags','anexo','cancelado']
    titulo = forms.CharField(error_messages={'required': 'Informe um titulo'},max_length=30, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus'}))
    data = forms.DateField(error_messages={'required': 'Informe a data do evento'},initial=date.today(),widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    inicio = forms.TimeField(required=False, widget=forms.TextInput(attrs={'class':'form-control','type':'time'}))
    termino = forms.TimeField(required=False, widget=forms.TextInput(attrs={'class':'form-control','type':'time'}))
    tags = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control tagin','placeholder':' '}))
    participantes = forms.ModelMultipleChoiceField(required=False, queryset = User.objects.filter(is_active=True).order_by('username'))
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','style':'min-height:200px;','placeholder':' '}))
    local = forms.CharField(required=False, max_length=200, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    anexo = forms.FileField(required=False, widget=forms.ClearableFileInput(attrs={'class': 'form-control form-control-sm'}))

class FeriadoForm(forms.ModelForm):
    class Meta:
        model = Feriado
        fields = ['data','nome']
    data = forms.DateField(error_messages={'required': 'Informe uma data válida','unique':'<b>Erro:</b> Já existe feriado cadastrado nesta data'},initial=date.today(),widget=forms.TextInput(attrs={'class':'form-control','type':'date','autofocus':'autofocus'}))
    nome = forms.CharField(error_messages={'required': 'Informe o nome do feriado'}, max_length=30, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','first_name','last_name','email','is_superuser','is_staff','is_active']
    username = forms.CharField(error_messages={'required': 'Username requerido'},widget=forms.TextInput(attrs={'class': 'form-control fw-bold','placeholder':' ','autofocus':'autofocus'}))
    first_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    last_name = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','type':'email'}))
    is_superuser = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    is_staff = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    is_active = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name','permissions']
    name = forms.CharField(error_messages={'required': 'Nome do grupo requerido', 'unique': 'Grupo com este nome ja existe'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus'}))

class IssueForm(forms.ModelForm):
    class Meta:
        model = Issue
        fields = ['followers','assunto','historico','tipo','status','classificacao','avaliacao']
    tipo = forms.ChoiceField(required=False,choices=Issue.TIPO_CHOICES, widget=forms.Select(attrs={'class':'form-select','autofocus':'autofocus'}))
    assunto = forms.CharField(error_messages={'required': 'Informe o assunto'},max_length=85,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    status = forms.ChoiceField(choices=Issue.STATUS_CHOICES, widget=forms.Select(attrs={'class':'form-select readonly'}))
    classificacao = forms.ChoiceField(required=False, choices=Issue.CLASSIFICACAO_CHOICES, widget=forms.Select(attrs={'class':'form-select readonly'}))
    followers = forms.ModelMultipleChoiceField(queryset=User.objects.filter(is_active=True), required=False)


class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['gera_notificacao_issue_atualizado','quantidade_caracteres_senha','senha_exige_alpha','senha_exige_numero','senha_exige_caractere','historico_senhas_nao_repetir','bloqueia_conta_por_tentativas_erradas','quantidade_tentantivas_erradas','valida_senha_comum']
    gera_notificacao_issue_atualizado = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    quantidade_caracteres_senha = forms.IntegerField(required=False, initial=8, widget=forms.TextInput(attrs={'class': 'form-control form-control-sm','type':'number','min':'1','max':'90'}))
    senha_exige_alpha = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    senha_exige_numero = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    senha_exige_caractere = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    historico_senhas_nao_repetir = forms.IntegerField(required=False, initial=0, widget=forms.TextInput(attrs={'class': 'form-control form-control-sm','type':'number','min':'0','max':'10'}))
    bloqueia_conta_por_tentativas_erradas = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))
    quantidade_tentantivas_erradas = forms.IntegerField(required=False, initial=3, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'1','max':'10'}))
    valida_senha_comum = forms.BooleanField(required=False, initial=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input','role':'switch'}))