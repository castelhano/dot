from django.db import models
from django.contrib.auth.models import User, Group
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
    
class Alerta(models.Model):
    titulo = models.CharField(max_length=50, blank=True)
    mensagem = models.CharField(max_length=220, blank=True)
    link = models.CharField(max_length=220, blank=True)
    usuario = models.ForeignKey(User, on_delete=models.RESTRICT)
    lido = models.BooleanField(default=False)
    critico = models.BooleanField(default=False)
    alert_class_list = models.CharField(max_length=60, blank=True)
    action_class_list = models.CharField(max_length=60, blank=True)
    create_at = models.DateTimeField(default=datetime.now)
    lido_at = models.DateTimeField(blank=True, null=True)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    empresas = models.ManyToManyField(Empresa)
    force_password_change = models.BooleanField(default=True)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='auth.user',objeto_id=self.user.id).order_by('-data')[:15]
        return reversed(logs)
    def alertas(self):
        alertas = Alerta.objects.filter(to_user=self.user,lido=False).order_by('data')
        return alertas
    class Meta:
        permissions = [
            ("console", "Pode abrir o console"),
        ]


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

# EXTENDED **********************************************
class ImageField(models.ImageField):
    class Meta:
        abstract = True
    def save_form_data(self, instance, data):
        if data is not None: 
            file = getattr(instance, self.attname)
            if file != data:
                file.delete(save=False)
        super(ImageField, self).save_form_data(instance, data)

class FileField(models.FileField):
    class Meta:
        abstract = True
    def save_form_data(self, instance, data):
        if data is not None: 
            file = getattr(instance, self.attname)
            if file != data:
                file.delete(save=False)
        super(FileField, self).save_form_data(instance, data)