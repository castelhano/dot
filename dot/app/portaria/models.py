from django.db import models
from pessoal.models import Funcionario
from datetime import datetime, date
from core.models import Log, ImageField as core_ImageField

class Veiculo(models.Model):
    modelo = models.CharField(max_length=20, blank=False)
    cor = models.CharField(max_length=15, blank=True)
    placa = models.CharField(max_length=15, blank=False, unique=True)
    funcionario = models.ForeignKey(Funcionario, blank=True, null=True, on_delete=models.RESTRICT)
    valido_ate = models.DateField(blank=True, null=True, default = datetime.today)
    km_inicial = models.PositiveIntegerField(default=0, blank=True, null=True)
    def __str__(self):
        return str(self.id)
    def ativo(self):
        return True if self.valido_ate >= date.today() else False
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='portaria.veiculo',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)

class Area(models.Model):
    nome = models.CharField(max_length=20, blank=False, unique=True)
    css_breakpoint = models.CharField(max_length=200, blank=True)
    def __str__(self):
        return str(self.nome)
    def vagas(self):
        return Vaga.objects.filter(area=self).order_by('codigo')
    def vagas_ativas(self) :
        return Vaga.objects.filter(area=self, inativa=False).order_by('codigo')
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='portaria.area',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    class Meta:
        default_permissions = ('add','change','delete',)

class Vaga(models.Model):
    codigo = models.CharField(max_length=10, blank=False)
    area = models.ForeignKey(Area, blank=False, null=False, on_delete=models.RESTRICT)
    fixa = models.BooleanField(default=False)
    ocupada = models.BooleanField(default=False)
    inativa = models.BooleanField(default=True)
    detalhe = models.CharField(max_length=100, blank=True)
    def __str__(self):
        return self.codigo
    def disponivel(self):
        return False if self.ocupada or self.inativa else True
    def reservar(self):
        if not self.ocupada and not self.inativa:
            self.ocupada = True
            return [True]
        else:
            return [False, 'Vaga não está disponivel']
    def desocupar(self):
        if not self.ocupada:
            return [False, 'Vaga não está ocupada']
        self.ocupada = False
        return [True]
    def ocupante(self):
        if not self.ocupada:
            return None
        if RegistroFuncionario.objects.filter(vaga=self,data_saida=None).exists():
            return RegistroFuncionario.objects.filter(vaga=self,data_saida=None).get()
        if RegistroVisitante.objects.filter(vaga=self,data_saida=None).exists():
            return RegistroVisitante.objects.filter(vaga=self,data_saida=None).get()
    def ocupante_abbr(self):
        if not self.ocupada:
            return None
        if RegistroFuncionario.objects.filter(vaga=self,data_saida=None).exists():
            return RegistroFuncionario.objects.filter(vaga=self,data_saida=None).get().veiculo.funcionario.nome.split(' ')[0]
        if RegistroVisitante.objects.filter(vaga=self,data_saida=None).exists():
            return RegistroVisitante.objects.filter(vaga=self,data_saida=None).get().visitante.nome.split(' ')[0]
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='portaria.vaga',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    class Meta:
        permissions = [
            ("view_registro", "Visualizar registro"),
            ("add_registro", "Adicionar registro"),
            ("change_registro", "Atualizar registro"),
            ("delete_registro", "Excluir registro"),
        ]
    
class Visitante(models.Model):
    nome = models.CharField(max_length=100, blank=False)
    empresa = models.CharField(max_length=100, blank=True)
    rg = models.CharField(max_length=20, blank=True)
    cpf = models.CharField(max_length=20,blank=False, unique=True)
    fone1 = models.CharField(max_length=20, blank=True)
    fone2 = models.CharField(max_length=20, blank=True)
    email = models.CharField(max_length=150, blank=True)
    endereco = models.CharField(max_length=255, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=60, blank=True)
    uf = models.CharField(max_length=5, blank=True)
    foto = core_ImageField(upload_to='portaria/visitante/', blank=True)
    detalhe = models.TextField(blank=True)
    bloqueado = models.BooleanField(default=False)
    def __str__(self):
        return self.nome
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='portaria.visitante',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    def foto_url(self):
        return self.foto.url
    def foto_name(self):
        return self.foto.name.split('/')[-1]
    
            
class Registro(models.Model):
    vaga = models.ForeignKey(Vaga, blank=True, null=True, on_delete=models.RESTRICT)
    data_entrada = models.DateField(default = datetime.today)
    hora_entrada = models.TimeField(default = datetime.now)
    km_entrada = models.PositiveIntegerField(blank=True, null=True)
    data_saida = models.DateField(blank=True, null=True)
    hora_saida = models.TimeField(blank=True, null=True)
    km_saida = models.PositiveIntegerField(blank=True, null=True)
    detalhe = models.CharField(max_length=200, blank=True)
    class Meta:
        abstract = True

class RegistroFuncionario(Registro):
    veiculo = models.ForeignKey(Veiculo, blank=True, null=True, on_delete=models.RESTRICT)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='portaria.registro_funcionario',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    def ocupante_id(self):
        return self.veiculo.id
    class Meta:
        default_permissions = []

class RegistroVisitante(Registro):
    visitante = models.ForeignKey(Visitante, on_delete=models.RESTRICT)
    modelo = models.CharField(max_length=20, blank=True)
    cor = models.CharField(max_length=15, blank=True)
    placa = models.CharField(max_length=15, blank=True)
    autorizado_por = models.CharField(max_length=80, blank=True)
    def ultimas_alteracoes(self):
        logs = Log.objects.filter(modelo='portaria.registro_visitante',objeto_id=self.id).order_by('-data')[:15]
        return reversed(logs)
    def ocupante_id(self):
        return self.visitante.id
    class Meta:
        default_permissions = []