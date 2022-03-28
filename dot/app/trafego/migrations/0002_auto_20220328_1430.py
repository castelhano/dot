# Generated by Django 3.2.3 on 2022-03-28 18:30

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('oficina', '0001_initial'),
        ('pessoal', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
        ('trafego', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Agente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('matricula', models.CharField(max_length=15, unique=True)),
                ('nome', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Enquadramento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=15, unique=True)),
                ('nome', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Orgao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=40)),
            ],
        ),
        migrations.CreateModel(
            name='Notificacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(blank=True, choices=[('N', 'Notificacao'), ('G', 'Multa Gestor'), ('T', 'Multa Transito')], default='N', max_length=2)),
                ('codigo', models.CharField(blank=True, max_length=40)),
                ('data', models.DateField(default=datetime.datetime.today)),
                ('hora', models.TimeField(null=True)),
                ('valor', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('prazo', models.PositiveIntegerField(null=True)),
                ('detalhe', models.CharField(blank=True, max_length=200)),
                ('tratativa', models.TextField(blank=True)),
                ('created_on', models.DateField(blank=True, default=datetime.datetime.today, null=True)),
                ('agente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='trafego.agente')),
                ('create_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='usuario_notificacao_create', to=settings.AUTH_USER_MODEL)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='core.empresa')),
                ('enquadramento', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='trafego.enquadramento')),
                ('funcionario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='pessoal.funcionario')),
                ('linha', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='trafego.linha')),
                ('local', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='trafego.localidade')),
                ('validado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='usuario_notificacao_close', to=settings.AUTH_USER_MODEL)),
                ('veiculo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='oficina.frota')),
            ],
            options={
                'permissions': [('concluir_notificacao', 'Pode concluir notificacao')],
            },
        ),
        migrations.AddField(
            model_name='agente',
            name='orgao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='trafego.orgao'),
        ),
    ]
