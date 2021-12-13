from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.db.models.signals import post_save
from django.dispatch import receiver

class Empresa(models.Model):
    nome = models.CharField(max_length=50, unique=True, blank=False)
    razao_social = models.CharField(max_length=150, blank=True)
    cnpj = models.CharField(max_length=25, blank=True)
    inscricao_estadual = models.CharField(max_length=25, blank=True)
    inscricao_municipal = models.CharField(max_length=25, blank=True)
    cnae = models.CharField(max_length=20, blank=True)
    atividade = models.CharField(max_length=255, blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=60, blank=True)
    uf = models.CharField(max_length=5, blank=True)
    cep = models.CharField(max_length=10, blank=True)
    fone = models.CharField(max_length=20, blank=True)
    fax = models.CharField(max_length=20, blank=True)
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='core.empresa',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Log(models.Model):
    data = models.DateTimeField(default=datetime.now)
    modelo = models.CharField(max_length=50, blank=False)
    objeto_id = models.CharField(max_length=50, blank=False)
    objeto_str = models.CharField(max_length=50, blank=False)
    usuario = models.ForeignKey(User, on_delete=models.RESTRICT)
    mensagem = models.CharField(max_length=50, blank=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    empresas = models.ManyToManyField(Empresa)
    force_password_change = models.BooleanField(default=True)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='auth.user',objeto_id=self.user.id).order_by('-data')[:15]
        return reversed(logs)

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()