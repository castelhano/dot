from django import forms
from .models import Acidente, Oficina, Classificacao, Terceiro, TipoDespesa, Despesa, Forma, Termo
from datetime import date


class AcidenteForm(forms.ModelForm):
    class Meta:
        model = Acidente
        fields = ['empresa','pasta','classificacao','data','hora','veiculo','linha','condutor','inspetor','endereco','bairro','cidade','uf','culpabilidade','detalhe','concluido']
    pasta = forms.CharField(error_messages={'required': 'Informe uma identificação para a pasta','unique': 'Código de pasta já cadastrado'},widget=forms.TextInput(attrs={'class': 'form-control fw-bold','placeholder':' '}))
    classificacao = forms.ModelChoiceField(required=False, queryset = Classificacao.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select'}))
    data = forms.DateField(required=False,initial=date.today(),widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    hora = forms.TimeField(required=False, widget=forms.TextInput(attrs={'class':'form-control','type':'time'}))
    endereco = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    bairro = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    cidade = forms.CharField(required=False, initial='Cuiabá', widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    uf = forms.CharField(required=False, max_length=2, initial='MT', widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    culpabilidade = forms.ChoiceField(required=False,choices=Acidente.CULPABILIDADE_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','style':'min-height:200px;','placeholder':' '}))
    concluido = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class ClassificacaoForm(forms.ModelForm):
    class Meta:
        model = Classificacao
        fields = ['nome']
    nome = forms.CharField(error_messages={'required': 'Informe um nome para a classificação'}, max_length=30,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus'}))

class TerceiroForm(forms.ModelForm):
    class Meta:
        model = Terceiro
        fields = ['acidente','nome','classificacao','rg','cpf','fone1','fone2','email','endereco','bairro','cidade','uf','veiculo','placa','cor','ano','acordo','forma','oficina','concluido','pendente_nota_fiscal']
    nome = forms.CharField(error_messages={'required': 'Informe o nome do terceiro'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus'}))
    classificacao = forms.ChoiceField(required=False,choices=Terceiro.CLASSIFICACAO_CHOICES,initial='ENVOLVIDO', widget=forms.Select(attrs={'class':'form-select'}))
    rg = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    cpf = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    fone1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    fone2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','type':'email','placeholder':' '}))
    endereco = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    bairro = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    cidade = forms.CharField(required=False, initial='Cuiabá', widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    uf = forms.CharField(required=False, initial='MT', max_length=2,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    veiculo = forms.CharField(required=False, max_length=15,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    placa = forms.CharField(required=False,widget=forms.TextInput(attrs={'class':'form-control','placeholder':' '}))
    cor = forms.CharField(required=False, max_length=15,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    ano = forms.IntegerField(required=False, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'1980','max':'2100'}))
    acordo = forms.DecimalField(required=False,initial=0,widget=forms.TextInput(attrs={'class': 'form-control','onfocus':'this.select();'}))
    forma = forms.ModelChoiceField(required=False, queryset = Forma.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select'}))
    oficina = forms.ModelChoiceField(required=False, queryset = Oficina.objects.filter(ativa=True).order_by('nome'), widget=forms.Select(attrs={'class':'form-select'}))
    concluido = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    pendente_nota_fiscal = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class OficinaForm(forms.ModelForm):
    class Meta:
        model = Oficina
        fields = ['nome','contato','fone1','fone2','email','razao_social','cnpj','endereco','ativa']
    nome = forms.CharField(error_messages={'required': 'Informe o nome da oficina'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus'}))
    contato = forms.CharField(required=False,widget=forms.TextInput(attrs={'class':'form-control','placeholder':' '}))
    fone1 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':' '}))
    fone2 = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':' '}))
    email = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':' ','type':'email'}))
    endereco = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':' '}))
    razao_social = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':' '}))
    cnpj = forms.CharField(required=False, widget=forms.TextInput(attrs={'class':'form-control','placeholder':' '}))
    ativa = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class TipoDespesaForm(forms.ModelForm):
    class Meta:
        model = TipoDespesa
        fields = ['nome']
    nome = forms.CharField(error_messages={'required': 'Informe um nome para o tipo de despesa'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus'}))

class DespesaForm(forms.ModelForm):
    class Meta:
        model = Despesa
        fields = ['tipo','terceiro','data','valor','forma','detalhe']
    data = forms.DateField(error_messages={'required': 'Informe uma data válida'},initial=date.today(),widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    tipo = forms.ModelChoiceField(error_messages={'required': 'Informe um tipo para despesa'}, queryset = TipoDespesa.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select','autofocus':'autofocus'}))
    valor = forms.DecimalField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control','onfocus':'this.select();'}))
    forma = forms.ModelChoiceField(required=False, queryset = Forma.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select'}))
    detalhe = forms.CharField(required=False,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))

class FormaForm(forms.ModelForm):
    class Meta:
        model = Forma
        fields = ['nome']
    nome = forms.CharField(error_messages={'required': 'Informe o nome da forma de pagamento'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' ','autofocus':'autofocus'}))

class TermoForm(forms.ModelForm):
    class Meta:
        model = Termo
        fields = ['nome','titulo','representante','cargo','local','rodape']
    nome = forms.CharField(error_messages={'required': 'Informe um nome para o termo'},max_length=20,widget=forms.TextInput(attrs={'class': 'form-control fw-bold','placeholder':' ','autofocus':'autofocus'}))
    titulo = forms.CharField(required=False,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    representante = forms.CharField(required=False,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    cargo = forms.CharField(required=False,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    local = forms.CharField(required=False,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))
    rodape = forms.CharField(required=False,widget=forms.TextInput(attrs={'class': 'form-control','placeholder':' '}))