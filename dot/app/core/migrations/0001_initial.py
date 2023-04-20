# Generated by Django 4.1.2 on 2023-04-20 17:32

import core.models
import core.validators
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
                ('logo', core.models.ImageField(blank=True, upload_to='core/logos/')),
                ('footer', models.TextField(blank=True)),
            ],
            options={
                'permissions': [('dashboard_empresa', 'Pode usar o dashboard empresa')],
            },
        ),
        migrations.CreateModel(
            name='Feriado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(unique=True)),
                ('nome', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assunto', models.CharField(max_length=255)),
                ('historico', models.TextField(blank=True)),
                ('entrada', models.DateTimeField(default=datetime.datetime.now)),
                ('ultima_interacao', models.DateTimeField(default=datetime.datetime.now)),
                ('tipo', models.CharField(blank=True, choices=[('D', 'Duvida'), ('F', 'Falha / Erro'), ('M', 'Melhoria'), ('S', 'Sugestao')], max_length=3)),
                ('status', models.CharField(blank=True, choices=[('E', 'Em Espera'), ('A', 'Em Atendimento'), ('S', 'Aguardando Solicitante'), ('V', 'Pendente Validacao'), ('F', 'Fechado'), ('D', 'Em Desenvolvimento')], max_length=3)),
                ('classificacao', models.CharField(blank=True, choices=[('', '---'), ('bug', 'Crash'), ('logc', 'Logic'), ('perm', 'Permission'), ('ench', 'Enhancement'), ('unpr', 'Unproven')], max_length=5)),
                ('avaliacao', models.PositiveIntegerField(blank=True, null=True)),
                ('analista', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='analista', to=settings.AUTH_USER_MODEL)),
                ('followers', models.ManyToManyField(blank=True, related_name='issue_followers', to=settings.AUTH_USER_MODEL)),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='usuario', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('eh_suporte', 'Atuar como suporte')],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('force_password_change', models.BooleanField(default=True)),
                ('config', models.TextField(blank=True)),
                ('empresas', models.ManyToManyField(to='core.empresa')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('console', 'Pode abrir o console'), ('debug', 'DEBUG System'), ('docs', 'Acessar documentacao do sistema')],
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateTimeField(default=datetime.datetime.now)),
                ('modelo', models.CharField(max_length=50)),
                ('objeto_id', models.CharField(max_length=50)),
                ('objeto_related', models.CharField(blank=True, max_length=30)),
                ('objeto_str', models.CharField(max_length=50)),
                ('mensagem', models.CharField(blank=True, max_length=50)),
                ('usuario', models.ForeignKey(null=True, on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'default_permissions': ('view',),
            },
        ),
        migrations.CreateModel(
            name='Issuefile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', core.models.FileField(blank=True, upload_to='core/issue/%Y/%m/%d', validators=[core.validators.validate_file_extension])),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.issue')),
            ],
            options={
                'default_permissions': [],
            },
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
        migrations.CreateModel(
            name='Agenda',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(default=datetime.date.today)),
                ('inicio', models.TimeField(blank=True, null=True)),
                ('termino', models.TimeField(blank=True, null=True)),
                ('titulo', models.CharField(max_length=50)),
                ('detalhe', models.TextField(blank=True)),
                ('local', models.CharField(blank=True, max_length=220)),
                ('tags', models.CharField(blank=True, max_length=220)),
                ('anexo', core.models.FileField(blank=True, upload_to='core/agenda/anexos/%Y/%m/%d', validators=[core.validators.validate_excluded_files])),
                ('cancelado', models.BooleanField(default=False)),
                ('create_at', models.DateTimeField(default=datetime.datetime.now)),
                ('create_by', models.CharField(max_length=50)),
                ('participantes', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
