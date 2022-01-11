# Generated by Django 3.2.3 on 2022-01-11 21:01

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
            name='Empresa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
                ('razao_social', models.CharField(blank=True, max_length=150)),
                ('cnpj', models.CharField(blank=True, max_length=25)),
                ('inscricao_estadual', models.CharField(blank=True, max_length=25)),
                ('inscricao_municipal', models.CharField(blank=True, max_length=25)),
                ('cnae', models.CharField(blank=True, max_length=20)),
                ('atividade', models.CharField(blank=True, max_length=255)),
                ('endereco', models.CharField(blank=True, max_length=255)),
                ('bairro', models.CharField(blank=True, max_length=100)),
                ('cidade', models.CharField(blank=True, max_length=60)),
                ('uf', models.CharField(blank=True, max_length=5)),
                ('cep', models.CharField(blank=True, max_length=10)),
                ('fone', models.CharField(blank=True, max_length=20)),
                ('fax', models.CharField(blank=True, max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('force_password_change', models.BooleanField(default=True)),
                ('empresas', models.ManyToManyField(to='core.Empresa')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('console', 'Pode abrir o console')],
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(default=datetime.datetime.now)),
                ('modelo', models.CharField(max_length=50)),
                ('objeto_id', models.CharField(max_length=50)),
                ('objeto_str', models.CharField(max_length=50)),
                ('mensagem', models.CharField(blank=True, max_length=50)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Alerta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(blank=True, max_length=50)),
                ('mensagem', models.CharField(blank=True, max_length=220)),
                ('link', models.CharField(blank=True, max_length=220)),
                ('lido', models.BooleanField(default=False)),
                ('critico', models.BooleanField(default=False)),
                ('alert_class_list', models.CharField(blank=True, max_length=60)),
                ('action_class_list', models.CharField(blank=True, max_length=60)),
                ('create_at', models.DateTimeField(default=datetime.datetime.now)),
                ('lido_at', models.DateTimeField(blank=True, null=True)),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
