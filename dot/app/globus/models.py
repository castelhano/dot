from django.db import models
from datetime import datetime
from pessoal.models import Funcionario
from oficina.models import Frota
from trafego.models import Linha
from core.models import Empresa, Log
from django.contrib.auth.models import User


class Escala(models.Model):
    DIA_TIPO = (
    ('1','Util'),
    ('2','Sabado'),
    ('3','Domingo'),
    ('4','Ferias'),
    ('5','Especial'),
    )
    STATUS_CHOICES = (
    ('E','Escalado'),
    ('F','Folga'),
    ('C','Compensacao'),
    ('R','Ferias'),
    ('A','Fora de Escala'),
    )
    empresa = models.ForeignKey(Empresa, blank=True, null=True, on_delete=models.RESTRICT)
    status = models.CharField(max_length=3,choices=STATUS_CHOICES, blank=True, default='E')
    dia_tipo = models.CharField(max_length=3,choices=DIA_TIPO, blank=True, default='1')
    linha = models.ForeignKey(Linha, blank=True, null=True, on_delete=models.RESTRICT)
    nome_escala = models.CharField(max_length=40, blank=True)
    data = models.DateField(blank=True, null=True, default=datetime.today)
    tabela = models.CharField(max_length=10, blank=True)
    veiculo = models.ForeignKey(Frota, blank=True, null=True, on_delete=models.CASCADE)
    funcionario = models.ForeignKey(Funcionario, blank=True, null=True, on_delete=models.RESTRICT)
    inicio = models.TimeField(blank=True, null=True)
    termino = models.TimeField(blank=True, null=True)    
    local_pegada = models.CharField(max_length=50, blank=True, null=True)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='globus.escala',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    class Meta:
        permissions = [
            ("consultar_escala", "Consultar escala pessoal"),
            ("localizar_escala", "Consultar outras escalas"),
            ("parametrizar_escala", "Pode parametrizar escala"),
            ("importar_escala", "Pode importar escala"),
        ]

class Viagem(models.Model):
    SENTIDO_CHOICES = (
    ('','-----'),
    ('1','Ida'),
    ('2','Volta'),
    )
    escala = models.ForeignKey(Escala, on_delete=models.CASCADE)
    origem = models.CharField(max_length=50, blank=True)
    destino = models.CharField(max_length=50, blank=True)
    produtiva = models.BooleanField(default=True)
    sentido = models.CharField(max_length=3,choices=SENTIDO_CHOICES, blank=True, default='')
    inicio = models.TimeField(blank=True, null=True)
    termino = models.TimeField(blank=True, null=True)
    extra = models.BooleanField(default=False)