# Generated by Django 4.1.2 on 2023-05-19 20:35

import arquivo.models
import arquivo.validators
import core.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pessoal', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ativo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entrada', models.DateField(blank=True, null=True)),
                ('vencimento', models.DateField(blank=True, null=True)),
                ('responsavel', models.CharField(blank=True, max_length=100)),
                ('chaves', models.CharField(blank=True, max_length=150)),
                ('fisico', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('A', 'Arquivo'), ('R', 'Retirado'), ('D', 'Descartado')], default='A', max_length=3)),
                ('descarte', models.TextField(blank=True)),
            ],
            options={
                'permissions': [('descartar_ativo', 'Pode descartar')],
            },
        ),
        migrations.CreateModel(
            name='Container',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50, unique=True)),
                ('capacidade', models.PositiveIntegerField(default=0)),
                ('inativo', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Grupo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=80, unique=True)),
                ('tempo_guarda', models.PositiveIntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Limite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('empresa', models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, to='core.empresa')),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', core.models.FileField(blank=True, upload_to=arquivo.models.get_file_path, validators=[arquivo.validators.validate_excluded_files])),
                ('ativo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='arquivo.ativo')),
            ],
            options={
                'default_permissions': ('view', 'add', 'delete'),
            },
        ),
        migrations.AddField(
            model_name='ativo',
            name='container',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='arquivo.container'),
        ),
        migrations.AddField(
            model_name='ativo',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='ativo',
            name='empresa',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='core.empresa'),
        ),
        migrations.AddField(
            model_name='ativo',
            name='grupo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='arquivo.grupo'),
        ),
        migrations.AddField(
            model_name='ativo',
            name='setor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='pessoal.setor'),
        ),
    ]
