from django.db import models
from django.db.models import Sum
from datetime import datetime
from oficina.models import Frota
from core.models import Empresa, Log
from trafego.models import Linha
from pessoal.models import Funcionario
from django.contrib.auth.models import User

class Classificacao(models.Model):
    nome = models.CharField(max_length=50, unique=True, blank=False)
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='sinistro.classificacao',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Acidente(models.Model):
    CULPABILIDADE_CHOICES = (
    ('','Indefinido'),
    ('E','Empresa'),
    ('T','Terceiro'),
    )
    empresa = models.ForeignKey(Empresa, blank=True, null=True, on_delete=models.RESTRICT)
    pasta = models.CharField(max_length=10, unique=True, blank=False)
    classificacao = models.ForeignKey(Classificacao, blank=True, null=True, on_delete=models.PROTECT)
    data = models.DateField(blank=True, null=True)
    hora = models.TimeField(blank=True, null=True)
    veiculo = models.ForeignKey(Frota, blank=True, null=True, on_delete=models.PROTECT)
    linha = models.ForeignKey(Linha, blank=True, null=True, on_delete=models.PROTECT)
    condutor = models.ForeignKey(Funcionario, blank=True, null=True, related_name='acidente_condutor', on_delete=models.PROTECT)
    inspetor = models.ForeignKey(Funcionario, blank=True, null=True, related_name='acidente_inspetor', on_delete=models.PROTECT)
    endereco = models.CharField(max_length=255, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=60, blank=True)
    uf = models.CharField(max_length=5, blank=True)
    culpabilidade = models.CharField(max_length=4,choices=CULPABILIDADE_CHOICES, blank=True)
    detalhe = models.TextField(blank=True)
    concluido = models.BooleanField(default=False)
    created_on = models.DateField(blank=True, null=True, default=datetime.today)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.RESTRICT)
    def __str__(self):
        return self.pasta
    def acordos(self):
        valor = Terceiro.objects.filter(sinistro=self).aggregate(Sum('acordo'))
        if valor['acordo__sum'] == None:
            return 0
        else:
            return float(valor['acordo__sum'])
    def despesas(self):
        valor = Despesa.objects.filter(terceiro__sinistro=self).aggregate(Sum('valor'))
        if valor['valor__sum'] == None:
            return 0
        else:
            return float(valor['valor__sum'])
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='sinistro.acidente',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    class Meta:
        permissions = [
            ("tratar_acidente", "Tratar acidentes de outros inspetores"),
        ]

class Foto(models.Model):
    acidente = models.ForeignKey(Acidente, on_delete=models.CASCADE)
    foto = models.ImageField(upload_to="sinistro/%Y/%m/%d")
    def url(self):
        return self.foto.url
    def url_abbr(self):
        return self.foto.url.replace("/media/sinistro/","")


class Oficina(models.Model):
    nome = models.CharField(max_length=100, unique=True, blank=False)
    contato = models.CharField(max_length=80, blank=True)
    fone1 = models.CharField(max_length=20, blank=True)
    fone2 = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=150, blank=True)
    razao_social = models.CharField(max_length=200, blank=True)
    cnpj = models.CharField(max_length=20, blank=True)
    endereco = models.CharField(max_length=200, blank=True)
    ativa = models.BooleanField(default=True)
    def __str__(self):
        return self.nome
    def notasPendentes(self):
        notas = Terceiro.objects.filter(oficina=self,status='NF')
        qtde = notas.count()
        soma = notas.aggregate(Sum('acordo'))['acordo__sum']
        return [qtde,soma]
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='sinistro.oficina',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Forma(models.Model):
    nome = models.CharField(max_length=90, unique=True, blank=False)
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='sinistro.forma',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Terceiro(models.Model):
    CLASSIFICACAO_CHOICES = (
    ('EN','Envolvido'),
    ('VT','Vitima'),
    ('FT','Vitima Fatal'),
    )
    sinistro = models.ForeignKey(Acidente, on_delete=models.PROTECT)
    nome = models.CharField(max_length=200, blank=False)
    classificacao = models.CharField(max_length=4,choices=CLASSIFICACAO_CHOICES, blank=True)
    rg = models.CharField(max_length=20, blank=True)
    cpf = models.CharField(max_length=20, blank=True)
    fone1 = models.CharField(max_length=20, blank=True)
    fone2 = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=150, blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=60, blank=True)
    uf = models.CharField(max_length=5, blank=True)
    veiculo = models.CharField(max_length=30, blank=True)
    placa = models.CharField(max_length=15, blank=True)
    cor = models.CharField(max_length=20, blank=True)
    ano = models.PositiveIntegerField(blank=True, null=True)
    acordo = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    forma = models.ForeignKey(Forma, blank=True, null=True, on_delete=models.PROTECT)
    oficina = models.ForeignKey(Oficina, blank=True, null=True, on_delete=models.PROTECT)
    concluido = models.BooleanField(default=False)
    pendente_nota_fiscal = models.BooleanField(default=False)
    def __str__(self):
        return self.nome
    def despesas(self):
        valor = Despesa.objects.filter(terceiro=self.id).aggregate(Sum('valor'))
        if valor['valor__sum'] == None:
            return 0
        else:
            return float(valor['valor__sum'])
    def custo_total(self):
        valor = Despesa.objects.filter(terceiro=self.id).aggregate(Sum('valor'))
        if valor['valor__sum'] == None:
            return 0
        else:
            return float(valor['valor__sum']) + float(self.acordo)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='sinistro.terceiro',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class TipoDespesa(models.Model):
    nome = models.CharField(max_length=100, unique=True, blank=False)
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='sinistro.tipodespesa',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)


class Despesa(models.Model):
    tipo = models.ForeignKey(TipoDespesa, on_delete=models.PROTECT)
    terceiro = models.ForeignKey(Terceiro, on_delete=models.PROTECT)
    data = models.DateField(blank=True, null=True, default=datetime.today)
    valor = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    forma = models.ForeignKey(Forma,blank=True, null=True, on_delete=models.PROTECT)
    detalhe = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='sinistro.despesa',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)


class Termo(models.Model):
    nome = models.CharField(max_length=100, unique=True, blank=False)
    titulo = models.CharField(max_length=60, blank=True)
    representante = models.CharField(max_length=40, blank=True)
    cargo = models.CharField(max_length=40, blank=True)
    local = models.CharField(max_length=40, blank=True)
    rodape = models.CharField(max_length=150, blank=True)
    created_on = models.DateField(blank=True, null=True, default=datetime.today)
    author = models.ForeignKey(User, blank=True, null=True, on_delete=models.RESTRICT)
    def __str__(self):
        return self.nome
    def paragrafos(self):
        return Paragrafo.objects.filter(termo=self).count()
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='sinistro.termo',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Paragrafo(models.Model):
    termo = models.ForeignKey(Termo, on_delete=models.CASCADE)
    ordem = models.PositiveIntegerField(blank=False, null=False)
    texto = models.TextField(blank=True)
