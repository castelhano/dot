# Generated by Django 4.1.1 on 2023-02-04 22:20

import core.models
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import sinistro.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pessoal', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
        ('oficina', '0001_initial'),
        ('trafego', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Acidente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pasta', models.CharField(max_length=10, unique=True)),
                ('data', models.DateField(blank=True, null=True)),
                ('hora', models.TimeField(blank=True, null=True)),
                ('endereco', models.CharField(blank=True, max_length=255)),
                ('bairro', models.CharField(blank=True, max_length=100)),
                ('cidade', models.CharField(blank=True, max_length=60)),
                ('uf', models.CharField(blank=True, max_length=5)),
                ('culpabilidade', models.CharField(blank=True, choices=[('', 'Indefinido'), ('E', 'Empresa'), ('T', 'Terceiro')], max_length=4)),
                ('detalhe', models.TextField(blank=True)),
                ('concluido', models.BooleanField(default=False)),
                ('created_on', models.DateField(blank=True, default=datetime.datetime.today, null=True)),
            ],
            options={
                'permissions': [('tratar_acidente', 'Tratar acidentes de outros inspetores'), ('dashboard_acidente', 'Pode acessar dashboard acidentes')],
            },
        ),
        migrations.CreateModel(
            name='Classificacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Forma',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=90, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Oficina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
                ('contato', models.CharField(blank=True, max_length=80)),
                ('fone1', models.CharField(blank=True, max_length=20)),
                ('fone2', models.CharField(blank=True, max_length=20)),
                ('email', models.CharField(blank=True, max_length=150)),
                ('razao_social', models.CharField(blank=True, max_length=200)),
                ('cnpj', models.CharField(blank=True, max_length=20)),
                ('endereco', models.CharField(blank=True, max_length=200)),
                ('ativa', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='TipoDespesa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Termo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100, unique=True)),
                ('titulo', models.CharField(blank=True, max_length=60)),
                ('representante', models.CharField(blank=True, max_length=40)),
                ('cargo', models.CharField(blank=True, max_length=40)),
                ('local', models.CharField(blank=True, max_length=40)),
                ('rodape', models.CharField(blank=True, max_length=150)),
                ('created_on', models.DateField(blank=True, default=datetime.datetime.today, null=True)),
                ('author', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Terceiro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=200)),
                ('classificacao', models.CharField(blank=True, choices=[('EN', 'Envolvido'), ('VT', 'Vitima'), ('FT', 'Vitima Fatal')], max_length=4)),
                ('rg', models.CharField(blank=True, max_length=20)),
                ('cpf', models.CharField(blank=True, max_length=20)),
                ('fone1', models.CharField(blank=True, max_length=20)),
                ('fone2', models.CharField(blank=True, max_length=20)),
                ('email', models.CharField(blank=True, max_length=150)),
                ('endereco', models.CharField(blank=True, max_length=255)),
                ('bairro', models.CharField(blank=True, max_length=100)),
                ('cidade', models.CharField(blank=True, max_length=60)),
                ('uf', models.CharField(blank=True, max_length=5)),
                ('veiculo', models.CharField(blank=True, max_length=30)),
                ('placa', models.CharField(blank=True, max_length=15)),
                ('cor', models.CharField(blank=True, max_length=20)),
                ('ano', models.PositiveIntegerField(blank=True, null=True)),
                ('acordo', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('concluido', models.BooleanField(default=False)),
                ('pendente_nota_fiscal', models.BooleanField(default=False)),
                ('acidente', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sinistro.acidente')),
                ('forma', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sinistro.forma')),
                ('oficina', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sinistro.oficina')),
            ],
        ),
        migrations.CreateModel(
            name='Paragrafo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordem', models.PositiveIntegerField()),
                ('texto', models.TextField(blank=True)),
                ('termo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sinistro.termo')),
            ],
            options={
                'default_permissions': ('add', 'change', 'delete'),
            },
        ),
        migrations.CreateModel(
            name='Foto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foto', models.ImageField(upload_to='sinistro/%Y/%m/%d')),
                ('acidente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sinistro.acidente')),
            ],
            options={
                'default_permissions': ('view', 'add', 'delete'),
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', core.models.FileField(blank=True, upload_to='sinistro/files/%Y/%m/%d', validators=[sinistro.validators.validate_excluded_files])),
                ('acidente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sinistro.acidente')),
            ],
            options={
                'default_permissions': ('view', 'add', 'delete'),
            },
        ),
        migrations.CreateModel(
            name='Despesa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(blank=True, default=datetime.datetime.today, null=True)),
                ('valor', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('detalhe', models.CharField(blank=True, max_length=100)),
                ('forma', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sinistro.forma')),
                ('terceiro', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sinistro.terceiro')),
                ('tipo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sinistro.tipodespesa')),
            ],
        ),
        migrations.AddField(
            model_name='acidente',
            name='classificacao',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='sinistro.classificacao'),
        ),
        migrations.AddField(
            model_name='acidente',
            name='condutor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='acidente_condutor', to='pessoal.funcionario'),
        ),
        migrations.AddField(
            model_name='acidente',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='acidente',
            name='empresa',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='core.empresa'),
        ),
        migrations.AddField(
            model_name='acidente',
            name='inspetor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='acidente_inspetor', to='pessoal.funcionario'),
        ),
        migrations.AddField(
            model_name='acidente',
            name='linha',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='trafego.linha'),
        ),
        migrations.AddField(
            model_name='acidente',
            name='veiculo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='oficina.frota'),
        ),
    ]
