from django import forms
from .models import Linha, Localidade



class LocalidadeForm(forms.ModelForm):
    class Meta:
        model = Localidade
        fields = ['nome','eh_garagem','troca_turno']
    nome = forms.CharField(error_messages={'required': 'Defina um nome para localidade'},widget=forms.TextInput(attrs={'class': 'form-control','autofocus':'autofocus','placeholder':''}))
    eh_garagem = forms.BooleanField(required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    troca_turno = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

class LinhaForm(forms.ModelForm):
    class Meta:
        model = Linha
        fields = ['empresa','codigo','nome','classificacao','origem','destino','acesso_origem_km','acesso_destino_km','acesso_origem_minutos','acesso_destino_minutos','recolhe_origem_km','recolhe_destino_km','recolhe_origem_minutos','recolhe_destino_minutos','extensao_ida','extensao_volta','intervalo_ida','intervalo_volta', 'detalhe']
    codigo = forms.CharField(error_messages={'required': 'Campo Código OBRIGATÓRIO'},max_length=8,widget=forms.TextInput(attrs={'class': 'form-control bg-light fw-bold','placeholder':''}))
    nome = forms.CharField(error_messages={'required': 'É necessário informar um noma para linha'},widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    classificacao = forms.ChoiceField(choices=Linha.CLASSIFICACAO_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))
    origem = forms.ModelChoiceField(required=False, queryset = Localidade.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select'}))
    destino = forms.ModelChoiceField(required=False, queryset = Localidade.objects.all().order_by('nome'), widget=forms.Select(attrs={'class':'form-select'}))
    extensao_ida = forms.DecimalField(required=False,initial=0,min_value=0,max_digits=10,decimal_places=2,widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000','step':'.01', 'onfocus':'this.select();'}))
    extensao_volta = forms.DecimalField(required=False,initial=0,min_value=0,max_digits=10,decimal_places=2,widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000','step':'.01', 'onfocus':'this.select();'}))
    acesso_origem_km = forms.DecimalField(required=False,initial=0,min_value=0,max_digits=10,decimal_places=2,widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000','step':'.01', 'onfocus':'this.select();'}))
    acesso_destino_km = forms.DecimalField(required=False,initial=0,min_value=0,max_digits=10,decimal_places=2,widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000','step':'.01', 'onfocus':'this.select();'}))
    recolhe_origem_km = forms.DecimalField(required=False,initial=0,min_value=0,max_digits=10,decimal_places=2,widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000','step':'.01', 'onfocus':'this.select();'}))
    recolhe_destino_km = forms.DecimalField(required=False,initial=0,min_value=0,max_digits=10,decimal_places=2,widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000','step':'.01', 'onfocus':'this.select();'}))
    acesso_origem_minutos = forms.IntegerField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000', 'onfocus':'this.select();'}))
    acesso_destino_minutos = forms.IntegerField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000', 'onfocus':'this.select();'}))
    recolhe_origem_minutos = forms.IntegerField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000', 'onfocus':'this.select();'}))
    recolhe_destino_minutos = forms.IntegerField(required=False,initial=0, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'0','max':'1000', 'onfocus':'this.select();'}))
    intervalo_ida = forms.IntegerField(required=False,initial=5, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'1','max':'60', 'onfocus':'this.select();'}))
    intervalo_volta = forms.IntegerField(required=False,initial=5, widget=forms.TextInput(attrs={'class': 'form-control','type':'number','min':'1','max':'60', 'onfocus':'this.select();'}))
    detalhe = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control','placeholder':'Detalhes', 'rows':4,'tabindex':'-1'}))