# Generated by Django 4.0.2 on 2022-03-13 02:04

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pessoal', '0001_initial'),
        ('oficina', '0001_initial'),
        ('trafego', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Escala',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(blank=True, choices=[('E', 'Escalado'), ('P', 'Plantao'), ('F', 'Folga'), ('C', 'Compensacao'), ('R', 'Ferias'), ('A', 'Fora de Escala')], default='E', max_length=3)),
                ('dia_tipo', models.CharField(blank=True, choices=[('1', 'Util'), ('2', 'Sabado'), ('3', 'Domingo'), ('4', 'Ferias'), ('5', 'Especial')], default='1', max_length=3)),
                ('nome_escala', models.CharField(blank=True, max_length=40)),
                ('data', models.DateField(blank=True, default=datetime.datetime.today, null=True)),
                ('tabela', models.CharField(blank=True, max_length=10)),
                ('inicio', models.TimeField(blank=True, null=True)),
                ('termino', models.TimeField(blank=True, null=True)),
                ('local_pegada', models.CharField(blank=True, max_length=50, null=True)),
                ('log_importacao', models.CharField(blank=True, max_length=50, null=True)),
                ('empresa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='core.empresa')),
                ('funcionario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='pessoal.funcionario')),
                ('linha', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='trafego.linha')),
                ('veiculo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='oficina.frota')),
            ],
            options={
                'permissions': [('consultar_escala', 'Consultar escala pessoal'), ('localizar_escala', 'Consultar outras escalas'), ('importar_escala', 'Pode importar escala')],
            },
        ),
        migrations.CreateModel(
            name='Viagem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('origem', models.CharField(blank=True, max_length=50)),
                ('destino', models.CharField(blank=True, max_length=50)),
                ('produtiva', models.BooleanField(default=True)),
                ('sentido', models.CharField(blank=True, choices=[('', '-----'), ('I', 'Ida'), ('V', 'Volta')], default='', max_length=3)),
                ('inicio', models.TimeField(blank=True, null=True)),
                ('termino', models.TimeField(blank=True, null=True)),
                ('extra', models.BooleanField(default=False)),
                ('escala', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='globus.escala')),
            ],
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('consulta_escala_inicio', models.DateField(blank=True, default=None, null=True)),
                ('consulta_escala_fim', models.DateField(blank=True, default=None, null=True)),
                ('empresa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='core.empresa')),
            ],
        ),
    ]