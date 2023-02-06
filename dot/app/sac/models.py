from django.db import models
from datetime import date, datetime, timezone
from pessoal.models import Funcionario
from oficina.models import Frota
from trafego.models import Linha
from core.models import Empresa, Log
from django.contrib.auth.models import User

class Classificacao(models.Model):
    TIPO_CHOICES = (
        ('R','Reclamacao'),
        ('E','Elogio'),
        ('S','Sugestao'),
    )
    nome = models.CharField(max_length=50, unique=True, blank=False)
    tipo = models.CharField(max_length=3,choices=TIPO_CHOICES, default='R')
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='sac.classificacao',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)


class Reclamacao(models.Model):
    ORIGEM_CHOICES = (
        ('F','Fone'),
        ('S','Site'),
        ('G','Gestora'),
        ('O','Outro'),
    )
    PARECER_CHOICES = (
        ('','Em analise'),
        ('P','Procedente'),
        ('I','Improcedente'),
    )
    empresa = models.ForeignKey(Empresa, blank=True, null=True, on_delete=models.RESTRICT)
    origem = models.CharField(max_length=15, choices=ORIGEM_CHOICES, default='F')
    data = models.DateField(blank=True, null=True,default=date.today)
    hora = models.TimeField(blank=True, null=True)
    classificacao = models.ForeignKey(Classificacao, blank=True, null=True, on_delete=models.RESTRICT)
    veiculo = models.ForeignKey(Frota, blank=True, null=True, on_delete=models.RESTRICT)
    linha = models.ForeignKey(Linha, blank=True, null=True, on_delete=models.RESTRICT)
    funcionario = models.ForeignKey(Funcionario, blank=True, null=True, on_delete=models.RESTRICT)
    detalhe = models.TextField(blank=True)
    parecer = models.CharField(max_length=5,choices=PARECER_CHOICES, default='')
    reclamante = models.CharField(max_length=100, blank=True)
    fone1 = models.CharField(max_length=20, blank=True)
    fone2 = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=150, blank=True)
    tratado = models.BooleanField(default=False)
    retorno = models.TextField(blank=True)
    entrada = models.DateTimeField(blank=True, null=True, default=datetime.now)
    usuario = models.ForeignKey(User, blank=True, null=True, on_delete=models.RESTRICT)
    def dias_pendentes(self):
        return (datetime.now(timezone.utc) - self.entrada).days if not self.tratado else ''
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='sac.reclamacao',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Settings(models.Model):
    prazo_resposta = models.PositiveIntegerField(default=2, blank=True, null=True)
    class Meta:
        default_permissions = ('view','change',)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='sac.settings',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)