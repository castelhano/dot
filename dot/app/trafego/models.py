from django.db import models
from datetime import datetime
from core.models import Empresa, Log, ImageField as core_ImageField
from .validators import validate_file_extension
from oficina.models import Frota
from pessoal.models import Funcionario
from django.contrib.auth.models import User

class Localidade(models.Model):
    nome = models.CharField(max_length=80, unique=True, blank=False)
    eh_garagem = models.BooleanField(default=False)
    troca_turno = models.BooleanField(default=False)
    ponto_de_controle = models.BooleanField(default=False)
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='trafego.localidade',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Linha(models.Model):
    CLASSIFICACAO_CHOICES = (
    ('RD','Radial'),
    ('DM','Diametral'),
    ('CR','Circular'),
    ('TR','Troncal'),
    ('AL','Alimentadora'),
    ('IT','Intersetorial'),
    ('ES','Especial'),
    )
    STATUS_CHOICES = (
    ('A','Ativa'),
    ('I','Inativa'),
    )
    empresa = models.ForeignKey(Empresa, blank=True, null=True, on_delete=models.RESTRICT)
    codigo = models.CharField(max_length=8, unique=True, blank=False)
    nome = models.CharField(max_length=80, blank=False)
    classificacao = models.CharField(max_length=3,choices=CLASSIFICACAO_CHOICES, blank=True)
    origem = models.ForeignKey(Localidade,related_name='local_origem', blank=True, null=True, on_delete=models.RESTRICT)
    destino = models.ForeignKey(Localidade,related_name='local_destino', blank=True, null=True, on_delete=models.RESTRICT)
    acesso_origem_km = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    acesso_destino_km = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    acesso_origem_minutos = models.PositiveIntegerField(blank=True, null=True)
    acesso_destino_minutos = models.PositiveIntegerField(blank=True, null=True)
    recolhe_origem_km = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    recolhe_destino_km = models.DecimalField(default=0, max_digits=6, decimal_places=2)
    recolhe_origem_minutos = models.PositiveIntegerField(blank=True, null=True)
    recolhe_destino_minutos = models.PositiveIntegerField(blank=True, null=True)
    extensao_ida = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    extensao_volta = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    intervalo_ida = models.PositiveIntegerField(blank=True, null=True)
    intervalo_volta = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(max_length=3,default='A',choices=STATUS_CHOICES, blank=True)
    detalhe = models.TextField(blank=True)
    def __str__(self):
        return self.codigo
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='trafego.linha',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    def patamares(self):
        return Patamar.objects.filter(linha=self).order_by('inicial')
    class Meta:
        permissions = [
            ("dop_linha", "Pode acessar DOP"),
        ]

class Patamar(models.Model):
    linha = models.ForeignKey(Linha, blank=False, null=False, on_delete=models.CASCADE)
    # faixa = models.PositiveIntegerField(blank=False, null=False)
    inicial = models.PositiveIntegerField(blank=False, null=False)
    final = models.PositiveIntegerField(blank=False, null=False)
    ida = models.PositiveIntegerField(blank=True, null=True)
    volta = models.PositiveIntegerField(blank=True, null=True)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='trafego.patamar',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Planejamento(models.Model):
    STATUS_CHOICES = (
    ('A','Ativo'),
    ('I','Inativo'),
    )
    DIA_TIPO = (
    ('U','Util'),
    ('S','Sabado'),
    ('D','Domingo'),
    ('F','Ferias'),
    ('E','Especial'),
    )
    empresa = models.ForeignKey(Empresa, blank=False, null=False, on_delete=models.RESTRICT)
    linha = models.ForeignKey(Linha, blank=False, null=False, on_delete=models.RESTRICT)
    codigo = models.CharField(max_length=15, unique=True, blank=False)
    descricao = models.CharField(max_length=200, blank=True)
    dia_tipo = models.CharField(max_length=3,choices=DIA_TIPO, blank=True, default='U')
    usuario = models.ForeignKey(User, blank=True, null=True, on_delete=models.RESTRICT)
    data_criacao = models.DateField(blank=True, null=True, default=datetime.today)
    status = models.CharField(max_length=3,default='A',choices=STATUS_CHOICES, blank=True)
    pin = models.BooleanField(default=True)
    def __str__(self):
        return self.codigo
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='trafego.planejamento',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Carro(models.Model):
    CLASSIFICACAO_CHOICES = (
        ("","---"),
        ("AT","Articulado"),
        ("BI","Biarticulado"),
        ("ES","Especial"),
        ("MC","Microonibus"),
        ("MD","Midionibus"),
        ("CV","Convencional"),
        ("PD","Padron"),
    )
    planejamento = models.ForeignKey(Planejamento, blank=False, null=False, on_delete=models.CASCADE)
    classificacao = models.CharField(max_length=3,choices=CLASSIFICACAO_CHOICES, blank=True)
    cobrador = models.BooleanField(default=False)
    inclusivo = models.BooleanField(default=False)
    def viagens(self):
        return Viagem.objects.filter(carro=self)

class Viagem(models.Model):
    SENTIDO_CHOICES = (
    ('I','Ida'),
    ('V','Volta'),
    )
    TIPO_CHOICES = (
    ('1','1 Produtiva'),
    ('2','2 Expresso'),
    ('3','3 Semi Expresso'),
    ('5','5 Acesso'),
    ('6','6 Recolhe'),
    ('7','7 Intervalo'),
    ('0','0 Reservado'),
    )
    carro = models.ForeignKey(Carro, blank=False, null=False, on_delete=models.CASCADE)
    inicio = models.TimeField(blank=True, null=True)
    fim = models.TimeField(blank=True, null=True)
    sentido = models.CharField(max_length=3,choices=SENTIDO_CHOICES, blank=True, default='I')
    tipo = models.CharField(max_length=3,choices=TIPO_CHOICES, blank=True, default='1')
    dia_inicio = models.PositiveIntegerField(blank=True, null=True, default=1)
    dia_termino = models.PositiveIntegerField(blank=True, null=True, default=1)

class Evento(models.Model):
    nome = models.CharField(max_length=80, unique=True, blank=False)
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='trafego.evento',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Providencia(models.Model):
    nome = models.CharField(max_length=80, unique=True, blank=False)
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='trafego.providencia',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Ocorrencia(models.Model):
    GRAVIDADE_CHOICES = (
    ('L','Leve'),
    ('M','Medio'),
    ('G','Grave'),
    )
    empresa = models.ForeignKey(Empresa, blank=True, null=True, on_delete=models.RESTRICT)
    evento = models.ForeignKey(Evento, blank=False, null=False, on_delete=models.RESTRICT)
    data = models.DateField(blank=True, null=True, default=datetime.today)
    hora = models.TimeField(blank=True, null=True)
    linha = models.ForeignKey(Linha, blank=True, null=True, on_delete=models.RESTRICT)
    local = models.ForeignKey(Localidade, blank=True, null=True, on_delete=models.RESTRICT)
    veiculo = models.ForeignKey(Frota, blank=True, null=True, on_delete=models.RESTRICT)
    condutor = models.ForeignKey(Funcionario, blank=True, null=True, on_delete=models.RESTRICT)
    indisciplina_condutor = models.BooleanField(default=False)
    gravidade = models.CharField(max_length=2,choices=GRAVIDADE_CHOICES, blank=True, default='L')
    viagem_omitida = models.BooleanField(default=False)
    tratado = models.BooleanField(default=False)
    detalhe = models.TextField(blank=True)
    providencia = models.ForeignKey(Providencia, blank=True, null=True, on_delete=models.RESTRICT)
    usuario = models.ForeignKey(User, blank=True, null=True, on_delete=models.RESTRICT)
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='trafego.ocorrencia',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    def fotos(self):
        fotos = FotoOcorrencia.objects.filter(ocorrencia=self)
        return fotos
    class Meta:
        permissions = [
            ("dashboard_ocorrencia", "Pode ver dashboard ocorrencia"),
            ("tratar_ocorrencia", "Pode tratar ocorrencia"),
        ]

class FotoOcorrencia(models.Model):
    ocorrencia = models.ForeignKey(Ocorrencia, on_delete=models.CASCADE)
    foto = core_ImageField(upload_to='trafego/ocorrencias/%Y/%m/%d', validators=[validate_file_extension])
    def url(self):
        return self.foto.url
    def url_abbr(self):
        return self.foto.url.replace("/media/trafego/","")