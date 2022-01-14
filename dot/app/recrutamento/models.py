from django.db import models
from core.models import Log, FileField as core_FileField
from pessoal.models import Cargo
from .validators import validate_file_extension
from datetime import datetime, date, timedelta


class Vaga(models.Model):
    cargo = models.ForeignKey(Cargo, on_delete=models.RESTRICT)
    quantidade = models.PositiveIntegerField(default=0, blank=True, null=True)
    descricao = models.CharField(max_length=200, blank=True)
    visivel = models.BooleanField(default=True)
    def __str__(self):
        return self.cargo.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='recrutamento.vaga',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
        
class Candidato(models.Model):
    ORIGEM_CHOICES = (
    ('S','Site'),
    ('C','Cadastro'),
    )
    STATUS_CHOICES = (
    ('B','Banco'),
    ('S','Selecao'),
    ('C','Contratado'),
    ('D','Descartado'),
    )
    SEXO_CHOICES =(
    ('','Nao Informado'),
    ('M','Masculino'),
    ('F','Feminino'),
    )
    origem = models.CharField(max_length=3,choices=ORIGEM_CHOICES, blank=True, default='C')
    nome = models.CharField(max_length=200, blank=False)
    sexo = models.CharField(max_length=3,choices=SEXO_CHOICES, blank=True)
    rg = models.CharField(max_length=20, blank=True)
    cpf = models.CharField(max_length=20, unique=True, blank=True)
    vagas = models.ManyToManyField(Vaga, related_name="candidatos")
    data_nascimento = models.DateField(blank=True, null=True)
    endereco = models.CharField(max_length=255, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=60, blank=True)
    uf = models.CharField(max_length=5, blank=True)
    fone1 = models.CharField(max_length=20, blank=True)
    fone2 = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=150, blank=True)
    indicacao = models.CharField(max_length=50, blank=True)
    pne = models.BooleanField(default=False)
    status = models.CharField(max_length=3,choices=STATUS_CHOICES,default='B', blank=True)
    bloqueado_ate = models.DateField(blank=True, null=True)
    detalhe = models.TextField(blank=True)
    apresentacao = models.TextField(blank=True)
    curriculo = core_FileField(upload_to="recrutamento/curriculos/%Y/%m/%d",blank=True, validators=[validate_file_extension])
    create_at = models.DateTimeField(default=datetime.now)
    def __str__(self):
        return self.nome
    def bloqueado(self):
        if self.bloqueado_ate != None:
            result = True if self.bloqueado_ate >= date.today() else False
        else:
            result = False
        return result
    def vagas_disponiveis(self):
        return Vaga.objects.all().exclude(candidatos=self).order_by('cargo__nome')
    def idade(self):
        if self.data_nascimento:
            hoje = date.today()
            return hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        else:
            return ''
    def movimentar(self, operacao, **kwargs):
        self.status = operacao
        if operacao == 'C':
            try:
                Selecao.objects.filter(candidato=self, arquivar=False).update(resultado='A', arquivar=True)
                return True
            except:
                return False
        if kwargs.get('dias_bloqueio', None):
            try:
                self.bloqueado_ate = datetime.now() + timedelta(kwargs.get('dias_bloqueio'))
                return True
            except:
                return False
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='recrutamento.candidato',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    class Meta:
        permissions = [
            ("descartar_candidato", "Pode descartar / retornar candidato "),
            ("contratar_candidato", "Pode contratar candidato "),
        ]

class Selecao(models.Model):
    RESULTADO_CHOICES = (
    ('','---------'),
    ('A','Aprovado'),
    ('R','Reprovado'),
    )
    candidato = models.ForeignKey(Candidato, on_delete=models.CASCADE)
    data = models.DateField(default=datetime.today)
    hora = models.TimeField(blank=True, null=True)
    vaga = models.ForeignKey(Vaga, on_delete=models.RESTRICT)
    resultado = models.CharField(max_length=3,choices=RESULTADO_CHOICES, blank=True)
    arquivar = models.BooleanField(default=False)
    def __str__(self):
        return self.candidato
    def avaliacoes(self):
        return Avaliacao.objects.filter(selecao=self).order_by('criterio__nome')
    def movimentar(self, operacao):
        self.resultado = operacao
        if operacao == 'R':
            self.arquivar = True
        elif operacao == '':
            self.arquivar = False
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='recrutamento.selecao',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Criterio(models.Model):
    nome = models.CharField(max_length=80, blank=False)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='recrutamento.criterio',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Avaliacao(models.Model):
    STATUS_CHOICES = (
    ('','---------'),
    ('A','Aprovado'),
    ('R','Reprovado'),
    )
    selecao = models.ForeignKey(Selecao, on_delete=models.CASCADE)
    criterio = models.ForeignKey(Criterio, on_delete=models.RESTRICT)
    status = models.CharField(max_length=3,choices=STATUS_CHOICES, default='')
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='recrutamento.avaliacao',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Settings(models.Model):
    redirecinar_cadastro_ao_aprovar = models.BooleanField(default=True)
    descartar_reprovados = models.BooleanField(default=False)
    dias_bloqueio = models.PositiveIntegerField(default=90)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='recrutamento.settings',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)