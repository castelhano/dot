from django.db import models
from datetime import datetime, date
from core.models import Log, Empresa
from django.contrib.auth.models import User
from django.db.models import Avg


class Indicador(models.Model):
    nome = models.CharField(max_length=80, unique=True, blank=False)
    meta = models.DecimalField(default=None, max_digits=10, decimal_places=2, null=True)
    medida = models.CharField(max_length=6, blank=True)
    precisao = models.IntegerField(default=2)
    quanto_maior_melhor = models.BooleanField(default=True)
    ativo = models.BooleanField(default=True)
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='gestao.indicador',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    def get_apontamento(self, ref, empresa):
        try:
            return Apontamento.objects.get(indicador=self, referencia=ref, empresa__id=empresa)
        except Exception as e:
            return None
    def analises_pendentes(self, empresa):
        return Analise.objects.filter(indicador=self,empresa__id=empresa,concluido=False).exclude(tipo='L').order_by('created_on')
    def planos_ativos(self, empresa_id, somente_com_prazo=False):
        try:
            if somente_com_prazo:
                return Plano.objects.filter(diretriz__empresa__id=empresa_id, diretriz__ativo=True, diretriz__indicador=self).exclude(inicio=None).exclude(termino=None).order_by('inicio','termino')
            else:
                return Plano.objects.filter(diretriz__empresa__id=empresa_id, diretriz__ativo=True, diretriz__indicador=self).order_by('inicio','termino')
        except Exception as e:
            return None
    class Meta:
        default_permissions = []

class Apontamento(models.Model):
    EVOLUCAO_CHOICES = (
    (1,'Melhorou'),
    (0,'Manteve'),
    (-1,'Piorou'),
    )
    empresa = models.ForeignKey(Empresa, on_delete=models.RESTRICT)
    indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE)
    referencia = models.CharField(max_length=80, blank=False)
    valor = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    meta = models.DecimalField(default=None, max_digits=10, decimal_places=2, null=True)
    evolucao = models.IntegerField(choices=EVOLUCAO_CHOICES, blank=True, null=True)
    class Meta:
        default_permissions = ('add',)

class Staff(models.Model):
    ROLE_CHOICES = (
    ('M','Manager'),
    ('E','Estrategico'),
    ('G','Gerencial'),
    ('O','Operacional'),
    )
    usuario = models.OneToOneField(User, on_delete=models.RESTRICT)
    role = models.CharField(max_length=3,choices=ROLE_CHOICES, default='O')
    def __str__(self):
        return self.usuario.username
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='gestao.staff',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    def planos_em_progresso(self, empresa=None):
        if not empresa:
            if self.role in ['O','G']:
                return Plano.objects.filter(staff=self, status__in=['E','P'], diretriz__empresa__in=self.usuario.profile.empresas.all())
            else:
                return Plano.objects.filter(status__in=['E','P'], diretriz__empresa__in=self.usuario.profile.empresas.all())
        else:
            if self.role in ['O','G']:
                return Plano.objects.filter(staff=self, status__in=['E','P'], diretriz__empresa=empresa)
            else:
                return Plano.objects.filter(status__in=['E','P'], diretriz__empresa=empresa)
    def planos_em_avaliacao(self, empresa=None):
        if not empresa:
            if self.role in ['O','G']:
                return Plano.objects.filter(staff=self, status='A')
            else:
                return Plano.objects.filter(diretriz__empresa__in=self.usuario.profile.empresas.all(), status='A')
        else:
            if self.role in ['O','G']:
                return Plano.objects.filter(staff=self, status='A', diretriz__empresa=empresa)
            else:
                return Plano.objects.filter(diretriz__empresa=empresa, status='A')
            
    def planos_arquivados(self):
        if self.role in ['O','G']:
            return Plano.objects.filter(staff=self, status='C')
        else:
            return Plano.objects.filter(status='C')
    class Meta:
        default_permissions = []

class Label(models.Model):
    nome = models.CharField(max_length=20, unique=True, blank=False)
    cor = models.CharField(max_length=30, blank=True)
    fonte = models.CharField(max_length=30, blank=True)
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='gestao.label',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    class Meta:
        ordering = ('nome',)
    class Meta:
        default_permissions = []
    
class Analise(models.Model):
    TIPO_CHOICES = (
    ('L','Lembrete'),
    ('M','Melhoria'),
    ('N','Nao Conformidade'),
    )
    empresa = models.ForeignKey(Empresa, blank=True, null=True, on_delete=models.RESTRICT)
    indicador = models.ForeignKey(Indicador, on_delete=models.RESTRICT)
    tipo = models.CharField(max_length=3,choices=TIPO_CHOICES, default='L')
    descricao = models.TextField(blank=False)
    critico = models.BooleanField(default=False)
    concluido = models.BooleanField(default=False)
    created_on = models.DateField(blank=True, null=True, default=datetime.today)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.RESTRICT)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='gestao.analise',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    class Meta:
        default_permissions = []

class Diretriz(models.Model):
    empresa = models.ForeignKey(Empresa, on_delete=models.RESTRICT)
    indicador = models.ForeignKey(Indicador, on_delete=models.RESTRICT)
    analise = models.ForeignKey(Analise, blank=True, null=True, on_delete=models.RESTRICT)
    titulo = models.CharField(max_length=100, blank=False)
    detalhe = models.TextField(blank=True)
    ativo = models.BooleanField(default=True)
    created_on = models.DateField(blank=True, null=True, default=datetime.today)
    created_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.RESTRICT)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='gestao.diretriz',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    def planos(self):
        return Plano.objects.filter(diretriz=self).order_by('inicio','termino')
    def progresso(self):
        try:
            return int(Plano.objects.filter(diretriz=self).aggregate(Avg('conclusao'))['conclusao__avg'])
        except Exception as e:
            return 0
    class Meta:
        permissions = [
            ("dashboard", "Pode ver dashboard"),
            ("staff", "Gerir a Staff"),
            ("view_kanban", "Visualizar Kanban"),
            ("change_kanban", "Editar Kanban")
        ]
        default_permissions = []
    
class Plano(models.Model):
    STATUS_CHOICES = (
    ('E','Em andamento'),
    ('P','Prorrogado'),
    ('A','Avaliacao'),
    ('C','Concluido'),
    ('D','Cancelado'),
    )
    diretriz = models.ForeignKey(Diretriz, on_delete=models.RESTRICT)
    titulo = models.CharField(max_length=150, blank=False)
    detalhe = models.TextField(blank=True)
    inicio = models.DateField(blank=True, null=True, default=date.today)
    termino = models.DateField(blank=True, null=True)
    responsavel = models.ForeignKey(Staff, blank=True, null=True, related_name='plano_responsavel', on_delete=models.PROTECT)
    staff = models.ManyToManyField(Staff, related_name='plano_staff', blank=True)
    status = models.CharField(max_length=3,choices=STATUS_CHOICES, default='E')
    conclusao = models.IntegerField(default=0)
    avaliacao = models.IntegerField(default=0)
    labels = models.ManyToManyField(Label)
    bloqueado = models.BooleanField(default=False)
    created_on = models.DateField(blank=True, null=True, default=datetime.today)
    created_by = models.ForeignKey(User, related_name='plano_created_by', blank=True, null=True, on_delete=models.RESTRICT)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='gestao.plano',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    def staff_disponivel(self):
        if self.id:
            return Staff.objects.filter(usuario__profile__empresas=self.diretriz.empresa).exclude(usuario__is_active=False).exclude(id__in=self.staff.all())
        else:
            return Staff.objects.filter(usuario__profile__empresas=self.diretriz.empresa).exclude(usuario__is_active=False)
    def labels_disponiveis(self):
        if self.id:
            return Label.objects.all().exclude(id__in=self.labels.all())
        else:
            return Label.objects.all()
    class Meta:
        default_permissions = []

class Settings(models.Model):
    analytics_foco_mes_atual = models.BooleanField(default=False)
    gerar_alerta_nova_analise = models.BooleanField(default=True)
    gerar_alerta_nova_diretriz = models.BooleanField(default=True)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='gestao.settings',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    class Meta:
        default_permissions = []