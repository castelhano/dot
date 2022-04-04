# Generated by Django 4.0.2 on 2022-04-03 23:18

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Analise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descricao', models.TextField()),
                ('critico', models.BooleanField(default=False)),
                ('concluido', models.BooleanField(default=False)),
                ('created_on', models.DateField(blank=True, default=datetime.datetime.today, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='Diretriz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=100)),
                ('detalhe', models.TextField(blank=True)),
                ('ativo', models.BooleanField(default=True)),
                ('created_on', models.DateField(blank=True, default=datetime.datetime.today, null=True)),
                ('analise', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='gestao.analise')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('dashboard', 'Pode ver dashboard')],
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='Indicador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=80, unique=True)),
                ('meta', models.DecimalField(decimal_places=2, default=None, max_digits=10)),
                ('evolucao', models.IntegerField(blank=True, choices=[(1, 'Melhorou'), (0, 'Manteve'), (-1, 'Piorou')], null=True)),
                ('quanto_maior_melhor', models.BooleanField(default=True)),
                ('ativo', models.BooleanField(default=True)),
            ],
            options={
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=20, unique=True)),
                ('cor', models.CharField(blank=True, max_length=30)),
                ('fonte', models.CharField(blank=True, max_length=30)),
            ],
            options={
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('M', 'Manager'), ('E', 'Extrategico'), ('G', 'Gerencial'), ('O', 'Operacional')], default='O', max_length=3)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='Plano',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=150)),
                ('detalhe', models.TextField(blank=True)),
                ('inicio', models.DateField(blank=True, default=datetime.datetime.today, null=True)),
                ('termino', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('E', 'Em andamento'), ('P', 'Prorrogado'), ('A', 'Avaliação'), ('C', 'Concluido'), ('D', 'Cancelado')], default='E', max_length=3)),
                ('conclusao', models.IntegerField(default=0)),
                ('avaliacao', models.IntegerField(default=0)),
                ('created_on', models.DateField(blank=True, default=datetime.datetime.today, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='plano_created_by', to=settings.AUTH_USER_MODEL)),
                ('diretriz', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='gestao.diretriz')),
                ('labels', models.ManyToManyField(to='gestao.Label')),
                ('responsavel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='plano_responsavel', to='gestao.staff')),
                ('staff', models.ManyToManyField(blank=True, related_name='plano_staff', to='gestao.Staff')),
            ],
            options={
                'default_permissions': [],
            },
        ),
        migrations.AddField(
            model_name='diretriz',
            name='indicador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='gestao.indicador'),
        ),
        migrations.CreateModel(
            name='Apontamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('referencia', models.CharField(max_length=80)),
                ('valor', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('meta', models.DecimalField(decimal_places=2, default=None, max_digits=10)),
                ('indicador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestao.indicador')),
            ],
            options={
                'default_permissions': [],
            },
        ),
        migrations.AddField(
            model_name='analise',
            name='indicador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='gestao.indicador'),
        ),
    ]
