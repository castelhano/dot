from django.db import models
from core.models import Empresa, Log, ImageField as core_ImageField, FileField as core_FileField
from datetime import datetime, date
from .validators import validate_file_extension, validate_image_extension


class Marca(models.Model):
    nome = models.CharField(max_length=50, unique=True, blank=False)
    def __str__(self):
        return self.nome
    def ativos(self):
        return Frota.objects.filter(modelo__marca=self,status__in=['A','M','F']).count()
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='oficina.marca',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Classificacao(models.Model):
    nome = models.CharField(max_length=50, unique=True, blank=False)
    def __str__(self):
        return self.nome
    def ativos(self):
        return Frota.objects.filter(classificacao=self,status__in=['A','M','F']).count()
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='oficina.classificacao',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True, blank=False)
    def __str__(self):
        return self.nome
    def ativos(self):
        return Frota.objects.filter(categoria=self,status__in=['A','M','F']).count()
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='oficina.categoria',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Carroceria(models.Model):
    nome = models.CharField(max_length=50, unique=True, blank=False)
    def __str__(self):
        return self.nome
    def ativos(self):
        return Frota.objects.filter(carroceria=self,status__in=['A','M','F']).count()
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='oficina.carroceria',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Modelo(models.Model):
    nome = models.CharField(max_length=50, unique=True, blank=False)
    marca = models.ForeignKey(Marca, blank=True, null=True, on_delete=models.RESTRICT)
    def __str__(self):
        return self.nome
    def ativos(self):
        return Frota.objects.filter(modelo=self,status__in=['A','M','F']).count()
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='oficina.modelo',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    
class Componente(models.Model):
    nome = models.CharField(max_length=50, unique=True, blank=False)
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='oficina.componente',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    def ativos(self):
        ativos = Frota.objects.filter(componentes=self,status__in=['A','M','F']).count()
        return ativos

class Frota(models.Model):
    STATUS_CHOICES = (
        ("A","Ativo"),
        ("I","Inativo"),
        ("M","Em Manutencao"),
        ("F","Fora de Operacao"),
        ("V","Vendido"),
    )
    empresa = models.ForeignKey(Empresa, blank=True, null=True, on_delete=models.RESTRICT)
    prefixo = models.CharField(max_length=15, unique=True, blank=False)
    placa = models.CharField(max_length=15, blank=True)
    renavan = models.CharField(max_length=30, blank=True)
    chassi = models.CharField(max_length=50, blank=True)
    modelo = models.ForeignKey(Modelo, blank=True, null=True, on_delete=models.RESTRICT)
    categoria = models.ForeignKey(Categoria, blank=True, null=True, on_delete=models.RESTRICT)
    classificacao = models.ForeignKey(Classificacao, blank=True, null=True, on_delete=models.RESTRICT)
    carroceria = models.ForeignKey(Carroceria, blank=True, null=True, on_delete=models.RESTRICT)
    ano_fabricacao = models.PositiveIntegerField(default=0, blank=True, null=True)
    ano_modelo = models.PositiveIntegerField(default=0, blank=True, null=True)
    capacidade_tanque = models.PositiveIntegerField(default=0, blank=True, null=True)
    media_ideal = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    km_inicial = models.PositiveIntegerField(default=0, blank=True, null=True)
    catraca_inicial = models.PositiveIntegerField(default=0, blank=True, null=True)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='A', blank=True)
    aniversario = models.DateField(blank=True, null=True)
    inicio_operacao = models.DateField(blank=True, null=True)
    componentes = models.ManyToManyField(Componente, related_name="frota_componentes")
    data_venda = models.DateField(blank=True, null=True)
    crlv = core_FileField(upload_to="frota/files/crlv/",blank=True, validators=[validate_file_extension])
    foto_chassi = core_ImageField(upload_to='frota/files/chassi/', blank=True, validators=[validate_image_extension])
    comprador = models.CharField(max_length=255, blank=True)
    valor_venda = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    detalhe = models.TextField(blank=True)
    create_at = models.DateTimeField(default=datetime.now)
    def __str__(self):
        return self.prefixo
    def componentes_disponiveis(self):
        return Componente.objects.all().exclude(frota_componentes=self).order_by('nome')
    def idade_aniversario(self, simulado=date.today()):
        if self.aniversario:
            return ((simulado - self.aniversario).days / 365)
        else:
            return None
    def idade_ano_fabricacao(self, simulado=date.today()):
        if self.ano_fabricacao:
            return simulado.year - self.ano_fabricacao
        else:
            return None
    def idade_ano_modelo(self, simulado=date.today()):
        if self.ano_modelo:
            return simulado.year - self.ano_modelo
        else:
            return None
    def movimentar(self, operacao, **args):
        resp = {'A':'ATIVADO','I':'INATIVADO','M':'PARADO MANUTENCAO','F':'FORA OPERACAO'}
        if operacao in ['A', 'I', 'M', 'F']:
            self.status = operacao
            return resp[operacao]
        elif operacao == 'V':
            resp = 'VENDA FROTA' if self.status != 'V' else 'ALTERADO DADOS VENDA'
            self.status = 'V'
            self.data_venda = args['data_venda']
            self.comprador = args['comprador']
            self.valor_venda = args['valor_venda']
            return resp
        elif operacao == 'CV':
            self.status = 'A'
            self.data_venda = None
            self.comprador = ''
            self.valor_venda = 0
            return 'VENDA CANCELADA'
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='oficina.frota',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    class Meta:
        permissions = [
            ("alterar_prefixo", "Pode alterar prefixo"),
            ("vender_frota", "Pode vender frota"),
            ("movimentar_em_massa", "Pode movimentar em massa"),
            ("dashboard_frota", "Pode usar o dashboard frota"),
        ]