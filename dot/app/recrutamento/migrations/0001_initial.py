# Generated by Django 3.2.3 on 2022-01-13 12:57

import core.models
import datetime
from django.db import migrations, models
import django.db.models.deletion
import recrutamento.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pessoal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Candidato',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('origem', models.CharField(blank=True, choices=[('S', 'Site'), ('C', 'Cadastro')], default='C', max_length=3)),
                ('nome', models.CharField(max_length=200)),
                ('sexo', models.CharField(blank=True, choices=[('', 'Nao Informado'), ('M', 'Masculino'), ('F', 'Feminino')], max_length=3)),
                ('rg', models.CharField(blank=True, max_length=20)),
                ('cpf', models.CharField(blank=True, max_length=20, unique=True)),
                ('data_nascimento', models.DateField(blank=True, null=True)),
                ('endereco', models.CharField(blank=True, max_length=255)),
                ('bairro', models.CharField(blank=True, max_length=100)),
                ('cidade', models.CharField(blank=True, max_length=60)),
                ('uf', models.CharField(blank=True, max_length=5)),
                ('fone1', models.CharField(blank=True, max_length=20)),
                ('fone2', models.CharField(blank=True, max_length=20)),
                ('email', models.CharField(blank=True, max_length=150)),
                ('indicacao', models.CharField(blank=True, max_length=50)),
                ('pne', models.BooleanField(default=False)),
                ('status', models.CharField(blank=True, choices=[('B', 'Banco'), ('S', 'Selecao'), ('C', 'Contratado'), ('D', 'Descartado')], default='B', max_length=3)),
                ('bloqueado_ate', models.DateField(blank=True, null=True)),
                ('detalhe', models.TextField(blank=True)),
                ('apresentacao', models.TextField(blank=True)),
                ('curriculo', core.models.FileField(blank=True, upload_to='recrutamento/curriculos/%Y/%m/%d', validators=[recrutamento.validators.validate_file_extension])),
                ('mensagens', models.TextField(blank=True)),
                ('nova_mensagem', models.BooleanField(default=False)),
                ('bloquear_mensagens', models.BooleanField(default=False)),
                ('create_at', models.DateTimeField(default=datetime.datetime.now)),
            ],
            options={
                'permissions': [('descartar_candidato', 'Pode descartar / retornar candidato '), ('contratar_candidato', 'Pode contratar candidato ')],
            },
        ),
        migrations.CreateModel(
            name='Criterio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=80)),
            ],
        ),
        migrations.CreateModel(
            name='Vaga',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantidade', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('descricao', models.CharField(blank=True, max_length=200)),
                ('visivel', models.BooleanField(default=True)),
                ('cargo', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pessoal.cargo')),
            ],
        ),
        migrations.CreateModel(
            name='Selecao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=datetime.datetime.today)),
                ('resultado', models.CharField(blank=True, choices=[('', '---------'), ('A', 'Aprovado'), ('R', 'Reprovado')], max_length=3)),
                ('arquivar', models.BooleanField(default=False)),
                ('candidato', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recrutamento.candidato')),
                ('vaga', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='recrutamento.vaga')),
            ],
        ),
        migrations.AddField(
            model_name='candidato',
            name='vagas',
            field=models.ManyToManyField(related_name='candidatos', to='recrutamento.Vaga'),
        ),
        migrations.CreateModel(
            name='Avaliacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('', '---------'), ('A', 'Aprovado'), ('R', 'Reprovado')], default='', max_length=3)),
                ('criterio', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='recrutamento.criterio')),
                ('selecao', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recrutamento.selecao')),
            ],
        ),
    ]
