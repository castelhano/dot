# Generated by Django 4.1.2 on 2023-05-03 17:48

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Analise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('L', 'Lembrete'), ('M', 'Melhoria'), ('N', 'Nao Conformidade')], default='L', max_length=3)),
                ('descricao', models.TextField()),
                ('critico', models.BooleanField(default=False)),
                ('concluido', models.BooleanField(default=False)),
                ('created_on', models.DateField(blank=True, default=datetime.datetime.today, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='core.empresa')),
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
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='core.empresa')),
            ],
            options={
                'permissions': [('dashboard', 'Pode ver dashboard'), ('staff', 'Gerir a Staff'), ('view_kanban', 'Visualizar Kanban'), ('change_kanban', 'Editar Kanban')],
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='Indicador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=80, unique=True)),
                ('meta', models.DecimalField(decimal_places=2, default=None, max_digits=10, null=True)),
                ('medida', models.CharField(blank=True, max_length=6)),
                ('precisao', models.IntegerField(default=2)),
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
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('analytics_foco_mes_atual', models.BooleanField(default=False)),
            ],
            options={
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('M', 'Manager'), ('E', 'Estrategico'), ('G', 'Gerencial'), ('O', 'Operacional')], default='O', max_length=3)),
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
                ('inicio', models.DateField(blank=True, default=datetime.date.today, null=True)),
                ('termino', models.DateField(blank=True, null=True)),
                ('status', models.CharField(choices=[('E', 'Em andamento'), ('P', 'Prorrogado'), ('A', 'Avaliacao'), ('C', 'Concluido'), ('D', 'Cancelado')], default='E', max_length=3)),
                ('conclusao', models.IntegerField(default=0)),
                ('avaliacao', models.IntegerField(default=0)),
                ('bloqueado', models.BooleanField(default=False)),
                ('created_on', models.DateField(blank=True, default=datetime.datetime.today, null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='plano_created_by', to=settings.AUTH_USER_MODEL)),
                ('diretriz', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='gestao.diretriz')),
                ('labels', models.ManyToManyField(to='gestao.label')),
                ('responsavel', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='plano_responsavel', to='gestao.staff')),
                ('staff', models.ManyToManyField(blank=True, related_name='plano_staff', to='gestao.staff')),
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
                ('meta', models.DecimalField(decimal_places=2, default=None, max_digits=10, null=True)),
                ('evolucao', models.IntegerField(blank=True, choices=[(1, 'Melhorou'), (0, 'Manteve'), (-1, 'Piorou')], null=True)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='core.empresa')),
                ('indicador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gestao.indicador')),
            ],
            options={
                'default_permissions': ('add',),
            },
        ),
        migrations.AddField(
            model_name='analise',
            name='indicador',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='gestao.indicador'),
        ),
    ]
