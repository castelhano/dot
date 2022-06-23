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
    inicial = models.PositiveIntegerField(blank=False, null=False)
    final = models.PositiveIntegerField(blank=False, null=False)
    ida = models.PositiveIntegerField(blank=True, null=True)
    volta = models.PositiveIntegerField(blank=True, null=True)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='trafego.patamar',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    class Meta:
        default_permissions = [('change')]

class Planejamento(models.Model):
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
    patamares = models.TextField(blank=True)
    ativo = models.BooleanField(default=False)
    pin = models.BooleanField(default=True)
    def __str__(self):
        return self.codigo
    def carros(self):
        return Carro.objects.filter(planejamento=self)
    def qtd_carros(self):
        return Carro.objects.filter(planejamento=self).count()
    def viagens(self):
        return Viagem.objects.filter(carro__planejamento=self)
    def qtd_viagens(self):
        return Viagem.objects.filter(carro__planejamento=self).count()
    def qtd_viagens_produtivas(self):
        return Viagem.objects.filter(carro__planejamento=self, tipo__in=['1','2','3']).count()
    def qtd_viagens_improdutivas(self):
        return Viagem.objects.filter(carro__planejamento=self).exclude(tipo__in=['1','2','3','7']).count()
    def km_planejada(self):
        return self.km_produtivo() + self.km_ociosa() 
    def km_produtivo(self):
        viagens_ida = Viagem.objects.filter(carro__planejamento=self, sentido='I').exclude(tipo__in=['5','6','7']).count()
        viagens_volta = Viagem.objects.filter(carro__planejamento=self, sentido='V').exclude(tipo__in=['5','6','7']).count()
        return (viagens_ida * self.linha.extensao_ida) + (viagens_volta * self.linha.extensao_volta)
    def km_ociosa(self):
        acessos_ida = Viagem.objects.filter(carro__planejamento=self, sentido='I', tipo='5').count()
        acessos_volta = Viagem.objects.filter(carro__planejamento=self, sentido='V', tipo='5').count()
        recolhes_ida = Viagem.objects.filter(carro__planejamento=self, sentido='I', tipo='6').count()
        recolhes_volta = Viagem.objects.filter(carro__planejamento=self, sentido='V', tipo='6').count()
        return (acessos_ida * self.linha.acesso_origem_km) + (acessos_volta * self.linha.acesso_destino_km) + (recolhes_ida * self.linha.recolhe_origem_km) + (recolhes_volta * self.linha.recolhe_destino_km)
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
    class Meta:
        default_permissions = []

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
    ('9','9 Reservado'),
    )
    carro = models.ForeignKey(Carro, blank=False, null=False, on_delete=models.CASCADE)
    inicio = models.TimeField(blank=True, null=True)
    fim = models.TimeField(blank=True, null=True)
    sentido = models.CharField(max_length=3,choices=SENTIDO_CHOICES, blank=True, default='I')
    tipo = models.CharField(max_length=3,choices=TIPO_CHOICES, blank=True, default='1')
    dia_inicio = models.PositiveIntegerField(blank=True, null=True, default=1)
    dia_termino = models.PositiveIntegerField(blank=True, null=True, default=1)
    class Meta:
        default_permissions = []

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
    class Meta:
        default_permissions = [('add','view','delete')]

class Orgao(models.Model):
    nome = models.CharField(max_length=40, blank=False)
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='trafego.orgao',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Agente(models.Model):
    matricula = models.CharField(max_length=15, unique=True, blank=False)
    nome = models.CharField(max_length=50, blank=False)
    orgao = models.ForeignKey(Orgao, on_delete=models.RESTRICT)
    def __str__(self):
        return self.matricula
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='trafego.agente',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Enquadramento(models.Model):
    codigo = models.CharField(max_length=15, unique=True, blank=False)
    nome = models.CharField(max_length=50, blank=False)
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='trafego.enquadramento',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Predefinido(models.Model):
    abbr = models.CharField(max_length=80, blank=False)
    detalhe = models.TextField(blank=True)
    def __str__(self):
        return self.abbr
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='trafego.predefinido',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Notificacao(models.Model):
    TIPO_CHOICES = (
    ('N','Notificacao'),
    ('G','Multa Gestor'),
    ('T','Multa Transito'),
    )
    empresa = models.ForeignKey(Empresa, on_delete=models.RESTRICT)
    tipo = models.CharField(max_length=2,choices=TIPO_CHOICES, blank=True, default='N')
    codigo = models.CharField(max_length=40,blank=False,unique=True)
    data = models.DateField(default=datetime.today)
    hora = models.TimeField(null=True)
    veiculo = models.ForeignKey(Frota, blank=True, null=True, on_delete=models.RESTRICT)
    linha = models.ForeignKey(Linha, blank=True, null=True, on_delete=models.RESTRICT)
    funcionario = models.ForeignKey(Funcionario, blank=True, null=True, on_delete=models.RESTRICT)
    agente = models.ForeignKey(Agente, blank=True, null=True, on_delete=models.RESTRICT)
    enquadramento = models.ForeignKey(Enquadramento, blank=True, null=True, on_delete=models.RESTRICT)
    local = models.ForeignKey(Localidade, blank=True, null=True, on_delete=models.RESTRICT)
    valor = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    prazo = models.DateField(blank=True, null=True)
    detalhe = models.CharField(max_length=200,blank=True)
    tratativa = models.TextField(blank=True)
    veiculo_lacrado = models.BooleanField(default=False)
    validado_por = models.ForeignKey(User, related_name='usuario_notificacao_close', blank=True, null=True, on_delete=models.RESTRICT)
    created_on = models.DateField(blank=True, null=True, default=datetime.today)
    create_by = models.ForeignKey(User, related_name='usuario_notificacao_create', blank=True, null=True, on_delete=models.RESTRICT)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='trafego.notificacao',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    class Meta:
        permissions = [
            ("concluir_notificacao", "Pode concluir notificacao"),
        ]