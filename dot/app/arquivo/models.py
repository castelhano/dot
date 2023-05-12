import os
from django.db import models
from core.models import Empresa, Log, FileField as core_FileField
from pessoal.models import Setor
from .validators import validate_file_extension
from datetime import date
from django.contrib.auth.models import User

class Container(models.Model):
    nome = models.CharField(max_length=50, unique=True, blank=False)
    capacidade = models.PositiveIntegerField(default=0)
    inativo = models.BooleanField(default=False)
    def __str__(self):
        return self.nome
    def ativos(self):
        return Ativo.objects.filter(container=self).count()
    def ocupacao(self):
        ativos = Ativo.objects.filter(container=self).count()
        return ativos / self.capacidade * 100 if self.capacidade > 0 else 0
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='arquivo.container',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Grupo(models.Model):
    nome = models.CharField(max_length=80, unique=True, blank=False)
    tempo_guarda = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='arquivo.grupo',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)


class Limite(models.Model):
    empresa = models.OneToOneField(Empresa, on_delete=models.RESTRICT)
    quantidade = models.PositiveIntegerField(default=0, blank=True, null=True)
    def ativos(self):
        return Ativo.objects.filter(empresa=self.empresa, tipo='F', status='A').count()
    def ocupacao(self):
        ativos = Ativo.objects.filter(empresa=self.empresa,fisico=True, status='A').count()
        return ativos / self.quantidade * 100 if self.quantidade > 0 else 0
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='arquivo.limite',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Ativo(models.Model):
    STATUS_CHOICES = (
        ("A","Arquivo"),
        ("R","Retirado"),
        ("D","Descartado"),
    )
    empresa = models.ForeignKey(Empresa, on_delete=models.RESTRICT)
    setor = models.ForeignKey(Setor, blank=True, null=True, on_delete=models.RESTRICT)
    grupo = models.ForeignKey(Grupo, on_delete=models.RESTRICT)
    entrada = models.DateField(blank=True, null=True)
    vencimento = models.DateField(blank=True, null=True)
    responsavel = models.CharField(max_length=100, blank=True)
    chaves = models.CharField(max_length=150, blank=True)
    fisico = models.BooleanField(default=False)
    container = models.ForeignKey(Container, blank=True, null=True, on_delete=models.RESTRICT)
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, default='A')
    historico = models.TextField(blank=True)
    descarte = models.TextField(blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.RESTRICT)
    def keys(self):
        return self.chaves.split(";")
    def vencido(self):
        return True if self.vencimento <= date.today() else False
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='arquivo.ativo',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)


def get_file_path(instance, filename):
    return "arquivo/{}/{}".format(instance.ativo.empresa.id, filename)


class File(models.Model):
    ativo = models.ForeignKey(Ativo, on_delete=models.CASCADE)
    file = core_FileField(upload_to=get_file_path, blank=True, validators=[validate_file_extension])
    def url(self):
        return self.file.url
    def url_abbr(self):
        return self.file.url.replace("/media/arquivo/","")
    def extensao(self):
        return os.path.splitext(self.file.url)[1]
    def filename(self):
        return os.path.basename(self.file.name)
    class Meta:
        default_permissions = ('view','add','delete',)