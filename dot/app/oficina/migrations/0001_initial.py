# Generated by Django 4.1.2 on 2023-04-12 18:35

import core.models
import datetime
from django.db import migrations, models
import django.db.models.deletion
import oficina.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Carroceria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Classificacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Componente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Marca',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Modelo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
                ('marca', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='oficina.marca')),
            ],
        ),
        migrations.CreateModel(
            name='Frota',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prefixo', models.CharField(max_length=15, unique=True)),
                ('placa', models.CharField(blank=True, max_length=15)),
                ('renavan', models.CharField(blank=True, max_length=30)),
                ('chassi', models.CharField(blank=True, max_length=50)),
                ('ano_fabricacao', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('ano_modelo', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('capacidade_tanque', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('media_ideal', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('km_inicial', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('catraca_inicial', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('status', models.CharField(blank=True, choices=[('A', 'Ativo'), ('I', 'Inativo'), ('M', 'Em Manutencao'), ('F', 'Fora de Operacao'), ('V', 'Vendido')], default='A', max_length=3)),
                ('aniversario', models.DateField(blank=True, null=True)),
                ('inicio_operacao', models.DateField(blank=True, null=True)),
                ('data_venda', models.DateField(blank=True, null=True)),
                ('crlv', core.models.FileField(blank=True, upload_to='frota/files/crlv/', validators=[oficina.validators.validate_file_extension])),
                ('foto_chassi', core.models.ImageField(blank=True, upload_to='frota/files/chassi/', validators=[oficina.validators.validate_image_extension])),
                ('comprador', models.CharField(blank=True, max_length=255)),
                ('valor_venda', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('detalhe', models.TextField(blank=True)),
                ('create_at', models.DateTimeField(default=datetime.datetime.now)),
                ('carroceria', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='oficina.carroceria')),
                ('categoria', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='oficina.categoria')),
                ('classificacao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='oficina.classificacao')),
                ('componentes', models.ManyToManyField(related_name='frota_componentes', to='oficina.componente')),
                ('empresa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='core.empresa')),
                ('modelo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='oficina.modelo')),
            ],
            options={
                'permissions': [('alterar_prefixo', 'Pode alterar prefixo'), ('vender_frota', 'Pode vender frota'), ('movimentar_em_massa', 'Pode movimentar em massa'), ('dashboard_frota', 'Pode usar o dashboard frota')],
            },
        ),
    ]
