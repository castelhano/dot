# Generated by Django 3.2.3 on 2022-01-03 19:43

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cargo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
                ('atividades', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Setor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Funcionario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('apelido', models.CharField(blank=True, max_length=20)),
                ('nome_social', models.CharField(blank=True, max_length=100)),
                ('sexo', models.CharField(blank=True, choices=[('N', 'Nao Informado'), ('M', 'Masculino'), ('F', 'Feminino')], max_length=3)),
                ('data_nascimento', models.DateField(blank=True, null=True)),
                ('rg', models.CharField(blank=True, max_length=20)),
                ('rg_emissao', models.DateField(blank=True, null=True)),
                ('rg_orgao_expedidor', models.CharField(blank=True, max_length=15)),
                ('cpf', models.CharField(blank=True, max_length=20)),
                ('titulo_eleitor', models.CharField(blank=True, max_length=20)),
                ('titulo_zona', models.CharField(blank=True, max_length=10)),
                ('titulo_secao', models.CharField(blank=True, max_length=8)),
                ('reservista', models.CharField(blank=True, max_length=20)),
                ('cnh', models.CharField(blank=True, max_length=20)),
                ('cnh_categoria', models.CharField(blank=True, choices=[('', '----'), ('A', 'A'), ('B', 'B'), ('AB', 'AB'), ('C', 'C'), ('AC', 'AC'), ('D', 'D'), ('AD', 'AD'), ('E', 'E'), ('AE', 'AE'), ('ACC', 'ACC')], max_length=4)),
                ('cnh_primeira_habilitacao', models.DateField(blank=True, null=True)),
                ('cnh_emissao', models.DateField(blank=True, null=True)),
                ('cnh_validade', models.DateField(blank=True, null=True)),
                ('fone1', models.CharField(blank=True, max_length=20)),
                ('fone2', models.CharField(blank=True, max_length=20)),
                ('email', models.CharField(blank=True, max_length=150)),
                ('endereco', models.CharField(blank=True, max_length=255)),
                ('bairro', models.CharField(blank=True, max_length=100)),
                ('cidade', models.CharField(blank=True, max_length=60)),
                ('uf', models.CharField(blank=True, max_length=5)),
                ('estado_civil', models.CharField(blank=True, choices=[('S', 'Solteiro (a)'), ('C', 'Casado (a)'), ('D', 'Divorciado (a)'), ('V', 'Viuvo (a)')], max_length=3)),
                ('nome_mae', models.CharField(blank=True, max_length=150)),
                ('nome_pai', models.CharField(blank=True, max_length=150)),
                ('detalhe', models.TextField(blank=True)),
                ('matricula', models.CharField(max_length=15, unique=True)),
                ('regime', models.CharField(blank=True, choices=[('CLT', 'CLT'), ('PJ', 'Pessoa Juridica'), ('AP', 'Aprendiz')], default='CLT', max_length=5)),
                ('data_admissao', models.DateField(blank=True, default=datetime.datetime.today, null=True)),
                ('data_desligamento', models.DateField(blank=True, null=True)),
                ('motivo_desligamento', models.CharField(blank=True, choices=[('EM', 'Pelo Empregador'), ('JC', 'Por Justa Causa'), ('PD', 'Pedido de Desligamento'), ('RI', 'Rescisao Indireta'), ('AB', 'Abandono de Emprego'), ('DJ', 'Descisao Judicial')], max_length=3)),
                ('foto', models.ImageField(blank=True, upload_to='pessoal/fotos/')),
                ('status', models.CharField(blank=True, choices=[('A', 'ATIVO'), ('F', 'AFASTADO'), ('D', 'DESLIGADO')], default='A', max_length=3)),
                ('cargo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='pessoal.cargo')),
                ('empresa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='core.empresa')),
                ('usuario', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('associar_usuario', 'Pode associar usuario a funcionário'), ('afastar_funcionario', 'Pode afastar funcionário'), ('desligar_funcionario', 'Pode desligar funcionário')],
            },
        ),
        migrations.CreateModel(
            name='FuncaoFixa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(choices=[('M', 'Motorista'), ('A', 'Auxiliar'), ('T', 'Trafego'), ('O', 'Oficina')], max_length=3, unique=True)),
                ('cargos', models.ManyToManyField(related_name='ffixas', to='pessoal.Cargo')),
            ],
        ),
        migrations.CreateModel(
            name='Dependente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=230)),
                ('parentesco', models.CharField(blank=True, choices=[('C', 'Conjuge'), ('F', 'Filho / Enteado'), ('I', 'Irmao'), ('P', 'Pai / Mae'), ('S', 'Sogro / Sogra'), ('A', 'Avo / Bisavo'), ('N', 'Neto / Bisneto'), ('B', 'Bisneto'), ('In', 'Incapaz'), ('M', 'Outros menores')], default='F', max_length=3)),
                ('sexo', models.CharField(blank=True, choices=[('N', 'Nao Informado'), ('M', 'Masculino'), ('F', 'Feminino')], max_length=3)),
                ('data_nascimento', models.DateField(blank=True, null=True)),
                ('rg', models.CharField(blank=True, max_length=20)),
                ('rg_emissao', models.DateField(blank=True, null=True)),
                ('rg_orgao_expedidor', models.CharField(blank=True, max_length=15)),
                ('cpf', models.CharField(blank=True, max_length=20)),
                ('funcionario', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pessoal.funcionario')),
            ],
        ),
        migrations.AddField(
            model_name='cargo',
            name='setor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pessoal.setor'),
        ),
        migrations.CreateModel(
            name='Afastamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('motivo', models.CharField(blank=True, choices=[('D', 'Doenca'), ('A', 'Acidente Trabalho'), ('O', 'Outro')], default='D', max_length=3)),
                ('data_afastamento', models.DateField(blank=True, default=datetime.datetime.today, null=True)),
                ('data_retorno', models.DateField(blank=True, null=True)),
                ('reabilitado', models.BooleanField(default=False)),
                ('detalhe', models.TextField(blank=True)),
                ('funcionario', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pessoal.funcionario')),
            ],
        ),
    ]