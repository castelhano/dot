import os
from django.db import models
from django.conf import settings as ROOT
from django.contrib.auth.models import User
from datetime import date
from core.models import Empresa, Log, FileField as core_FileField
from pessoal.models import Setor
from .validators import validate_excluded_files

class Container(models.Model):
    nome = models.CharField(max_length=50, unique=True, blank=False)
    capacidade = models.PositiveIntegerField(default=0)
    inativo = models.BooleanField(default=False)
    def __str__(self):
        return self.nome
    def ativos(self):
        return Ativo.objects.filter(container=self).exclude(status='D').count()
    def ocupacao(self):
        ativos = Ativo.objects.filter(container=self).exclude(status='D').count()
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
        return Ativo.objects.filter(empresa=self.empresa, fisico=True, status='A').count()
    def ocupacao(self):
        ativos = Ativo.objects.filter(empresa=self.empresa,fisico=True, status='A').count()
        return ativos / self.quantidade * 100 if self.quantidade > 0 else 0
    def hd_usage(self):
        total = 0
        for dirpath, dirnames, filenames in os.walk(ROOT.MEDIA_ROOT + f'/arquivo/{self.empresa.id}'):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total += os.path.getsize(fp)
        return total
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
    descarte = models.TextField(blank=True)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.RESTRICT)
    def keys(self):
        return self.chaves.split(";")
    def vencido(self):
        return True if self.vencimento <= date.today() else False
    def files(self):
        return File.objects.filter(ativo=self)
    def descartar(self):
        self.status = 'D'
        files = File.objects.filter(ativo=self)
        for file in files:
            os.remove(file.file.path) # REMOVE ARQUIVO FISICO
            file.delete()
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='arquivo.ativo',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    class Meta:
        permissions = [
            ("descartar_ativo", "Pode descartar")
        ]


def get_file_path(instance, filename):
    return "arquivo/{}/{}/{}".format(instance.ativo.empresa.id, date.today().year, filename)


class File(models.Model):
    ativo = models.ForeignKey(Ativo, on_delete=models.CASCADE)
    file = core_FileField(upload_to=get_file_path, blank=True, validators=[validate_excluded_files])
    def url(self):
        return self.file.url
    def url_abbr(self):
        return self.file.url.replace("/media/arquivo/","")
    def extensao(self):
        return os.path.splitext(self.file.url)[1].replace('.','')
    def filename(self):
        return os.path.basename(self.file.name)
    class Meta:
        default_permissions = ('view','add','delete',)