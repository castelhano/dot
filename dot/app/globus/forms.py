from django import forms
from .models import Escala, Settings
from datetime import date


class EscalaForm(forms.ModelForm):
    class Meta:
        model = Escala
        fields = ['empresa','status','dia_tipo','linha','nome_escala','data','tabela','veiculo','funcionario','inicio','termino','local_pegada']
    status = forms.ChoiceField(required=False, choices=Escala.STATUS_CHOICES, widget=forms.Select(attrs={'class':'form-select'}))
    dia_tipo = forms.ChoiceField(required=False, choices=Escala.DIA_TIPO, widget=forms.Select(attrs={'class':'form-select'}))
    nome_escala = forms.CharField(required=False, max_length=20, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    data = forms.DateField(error_messages={'required': 'Informe a data da escala'}, initial=date.today(), widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    tabela = forms.CharField(required=False, max_length=8, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    local_pegada = forms.CharField(required=False, max_length=15, widget=forms.TextInput(attrs={'class': 'form-control','placeholder':''}))
    inicio = forms.TimeField(required=False, widget=forms.TextInput(attrs={'class':'form-control','type':'time'}))
    termino = forms.TimeField(required=False, widget=forms.TextInput(attrs={'class':'form-control','type':'time'}))

class SettingsForm(forms.ModelForm):
    class Meta:
        model = Settings
        fields = ['empresa','consulta_escala_inicio','consulta_escala_fim']
    consulta_escala_inicio = forms.DateField(required=False, widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    consulta_escala_fim = forms.DateField(required=False, widget=forms.TextInput(attrs={'class':'form-control','type':'date'}))
    def clean(self):
        cleaned_data = super().clean()
        consulta_escala_inicio = cleaned_data.get("consulta_escala_inicio")
        consulta_escala_fim = cleaned_data.get("consulta_escala_fim")
        if consulta_escala_fim < consulta_escala_inicio:
            raise forms.ValidationError("Data final precisa ser maior que inicial")