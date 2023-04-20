import os
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, date
from .validators import validate_excluded_files, validate_file_extension
from django.db.models.signals import post_save
from django.dispatch import receiver

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

# **********************************************

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
    logo = ImageField(upload_to="core/logos/", blank=True)
    footer = models.TextField(blank=True)
    def __str__(self):
        return self.nome
    def logo_filename(self):
        return os.path.basename(self.logo.name)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='core.empresa',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    class Meta:
        permissions = [
            ("dashboard_empresa", "Pode usar o dashboard empresa"),
        ]

class Log(models.Model):
    data = models.DateTimeField(default=datetime.now)
    modelo = models.CharField(max_length=50, blank=False)
    objeto_id = models.CharField(max_length=50, blank=False)
    objeto_related = models.CharField(max_length=30, blank=True)
    objeto_str = models.CharField(max_length=50, blank=False)
    usuario = models.ForeignKey(User, on_delete=models.RESTRICT, null=True)
    mensagem = models.CharField(max_length=50, blank=True)
    class Meta:
        default_permissions = ('view',)
    
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

class Agenda(models.Model):
    data = models.DateField(default=date.today)
    inicio = models.TimeField(blank=True, null=True)
    termino = models.TimeField(blank=True, null=True)
    titulo = models.CharField(max_length=50)
    detalhe = models.TextField(blank=True)
    participantes = models.ManyToManyField(User)
    local = models.CharField(max_length=220, blank=True)
    tags = models.CharField(max_length=220, blank=True)
    anexo = FileField(upload_to="core/agenda/anexos/%Y/%m/%d",blank=True, validators=[validate_excluded_files])
    cancelado = models.BooleanField(default=False)
    create_at = models.DateTimeField(default=datetime.now)
    create_by = models.CharField(max_length=50)
    def tags_as_list(self):
        return self.tags.split('/')
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='core.agenda',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    def anexo_filename(self):
        return os.path.basename(self.anexo.name)

class Feriado(models.Model):
    data = models.DateField(unique=True)
    nome = models.CharField(max_length=50)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='core.feriado',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Issue(models.Model):
    TIPO_CHOICES = (
        ('D','Duvida'),
        ('F','Falha / Erro'),
        ('M','Melhoria'),
        ('S','Sugestao')
    )
    STATUS_CHOICES = (
        ('E','Em Espera'),
        ('A','Em Atendimento'),
        ('S','Aguardando Solicitante'),
        ('V','Pendente Validacao'),
        ('F','Fechado'),
        ('D','Em Desenvolvimento')
    )
    CLASSIFICACAO_CHOICES = (
        ('','---'),
        ('bug','Crash'),
        ('logc','Logic'),
        ('perm','Permission'),
        ('ench','Enhancement'),
        ('unpr','Unproven')
    )
    usuario = models.ForeignKey(User, related_name='usuario', on_delete=models.RESTRICT, blank=True, null=True)
    analista = models.ForeignKey(User, related_name='analista', on_delete=models.RESTRICT, blank=True, null=True)
    followers = models.ManyToManyField(User, related_name='issue_followers', blank=True)
    assunto = models.CharField(max_length=255, blank=False)
    historico = models.TextField(blank=True)
    entrada = models.DateTimeField(default=datetime.now)
    ultima_interacao = models.DateTimeField(default=datetime.now)
    tipo = models.CharField(max_length=3,choices=TIPO_CHOICES, blank=True)
    status = models.CharField(max_length=3,choices=STATUS_CHOICES, blank=True)
    classificacao = models.CharField(max_length=5,choices=CLASSIFICACAO_CHOICES, blank=True)
    avaliacao = models.PositiveIntegerField(blank=True, null=True)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='core.issue',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    def tempo_em_espera(self):
        entrada = self.entrada.replace(tzinfo=None)
        # agora = datetime.now().replace(tzinfo=None)
        # print('NAIVE: ', entrada)
        # print('NOW: ', agora)
        return (datetime.utcnow() - entrada).total_seconds() / 60
    class Meta:
        permissions = [
            ("eh_suporte", "Atuar como suporte"),
        ]

class Issuefile(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    file = FileField(upload_to="core/issue/%Y/%m/%d", blank=True, validators=[validate_file_extension])
    def url_abbr(self):
        return self.file.url.replace("/media/core/issue/","")
    def file_name(self):
        return self.file.name.split('/')[-1]
    class Meta:
        default_permissions = []

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    empresas = models.ManyToManyField(Empresa)
    force_password_change = models.BooleanField(default=True)
    config = models.TextField(blank=True)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='auth.user',objeto_id=self.user.id).order_by('-data')[:15]
        return reversed(logs)
    def alertas(self):
        alertas = Alerta.objects.filter(to_user=self.user,lido=False).order_by('data')
        return alertas
    def allow_empresa(self, id): # Verifica se empresa esta habilitada para usuario
        return self.empresas.filter(pk=id).exists()
    class Meta:
        permissions = [
            ("console", "Pode abrir o console"),
            ("debug", "DEBUG System"),
            ("docs", "Acessar documentacao do sistema"),
        ]
        default_permissions = []

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()