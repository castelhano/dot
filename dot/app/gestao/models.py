from django.db import models
from datetime import datetime


class Apontamento(models.Model):
    referencia = models.DateField()
    valor = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    meta = models.DecimalField(default=None, max_digits=10, decimal_places=2)

class Indicador(models.Model):
    pass

class Staff(models.Model):
    pass
    
class Diretriz(models.Model):
    created_on = models.DateField(blank=True, null=True, default=datetime.today)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.RESTRICT)

class Plano(models.Model):
    pass

class Label(models.Model):
    pass

class Analise(models.Model):
    pass

class Analise(models.Model):
    pass