# Generated by Django 4.1.2 on 2023-08-01 14:02

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('trafego', '0001_initial'),
        ('core', '0001_initial'),
        ('oficina', '0001_initial'),
        ('pessoal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Classificacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
                ('tipo', models.CharField(choices=[('R', 'Reclamacao'), ('E', 'Elogio'), ('S', 'Sugestao')], default='R', max_length=3)),
            ],
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prazo_resposta', models.PositiveIntegerField(blank=True, default=2, null=True)),
            ],
            options={
                'default_permissions': ('view', 'change'),
            },
        ),
        migrations.CreateModel(
            name='Reclamacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('origem', models.CharField(choices=[('F', 'Fone'), ('S', 'Site'), ('G', 'Gestora'), ('O', 'Outro')], default='F', max_length=15)),
                ('data', models.DateField(blank=True, default=datetime.date.today, null=True)),
                ('hora', models.TimeField(blank=True, null=True)),
                ('detalhe', models.TextField(blank=True)),
                ('parecer', models.CharField(choices=[('', 'Em analise'), ('P', 'Procedente'), ('I', 'Improcedente')], default='', max_length=5)),
                ('reclamante', models.CharField(blank=True, max_length=100)),
                ('fone1', models.CharField(blank=True, max_length=20)),
                ('fone2', models.CharField(blank=True, max_length=20)),
                ('email', models.CharField(blank=True, max_length=150)),
                ('tratado', models.BooleanField(default=False)),
                ('retorno', models.TextField(blank=True)),
                ('entrada', models.DateTimeField(blank=True, default=datetime.datetime.now, null=True)),
                ('classificacao', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='sac.classificacao')),
                ('empresa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='core.empresa')),
                ('funcionario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='pessoal.funcionario')),
                ('linha', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='trafego.linha')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
                ('veiculo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='oficina.frota')),
            ],
        ),
    ]
