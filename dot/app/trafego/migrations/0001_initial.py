# Generated by Django 4.0.5 on 2022-06-29 18:42

import core.models
import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import trafego.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('oficina', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
        ('pessoal', '0001_initial'),
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
            name='Carro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('classificacao', models.CharField(blank=True, choices=[('', '---'), ('AT', 'Articulado'), ('BI', 'Biarticulado'), ('ES', 'Especial'), ('MC', 'Microonibus'), ('MD', 'Midionibus'), ('CV', 'Convencional'), ('PD', 'Padron')], max_length=3)),
                ('cobrador', models.BooleanField(default=False)),
                ('labels', models.CharField(blank=True, max_length=250)),
            ],
            options={
                'default_permissions': [],
            },
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
            name='Evento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=80, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Linha',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=8, unique=True)),
                ('nome', models.CharField(max_length=80)),
                ('classificacao', models.CharField(blank=True, choices=[('RD', 'Radial'), ('DM', 'Diametral'), ('CR', 'Circular'), ('TR', 'Troncal'), ('AL', 'Alimentadora'), ('IT', 'Intersetorial'), ('ES', 'Especial')], max_length=3)),
                ('acesso_origem_km', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('acesso_destino_km', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('acesso_origem_minutos', models.PositiveIntegerField(blank=True, null=True)),
                ('acesso_destino_minutos', models.PositiveIntegerField(blank=True, null=True)),
                ('recolhe_origem_km', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('recolhe_destino_km', models.DecimalField(decimal_places=2, default=0, max_digits=6)),
                ('recolhe_origem_minutos', models.PositiveIntegerField(blank=True, null=True)),
                ('recolhe_destino_minutos', models.PositiveIntegerField(blank=True, null=True)),
                ('extensao_ida', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('extensao_volta', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('intervalo_ida', models.PositiveIntegerField(blank=True, null=True)),
                ('intervalo_volta', models.PositiveIntegerField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('A', 'Ativa'), ('I', 'Inativa')], default='A', max_length=3)),
                ('detalhe', models.TextField(blank=True)),
            ],
            options={
                'permissions': [('dop_linha', 'Pode acessar DOP')],
            },
        ),
        migrations.CreateModel(
            name='Localidade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=80, unique=True)),
                ('eh_garagem', models.BooleanField(default=False)),
                ('troca_turno', models.BooleanField(default=False)),
                ('ponto_de_controle', models.BooleanField(default=False)),
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
            name='Predefinido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abbr', models.CharField(max_length=80)),
                ('detalhe', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Providencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=80, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Viagem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inicio', models.TimeField(blank=True, null=True)),
                ('fim', models.TimeField(blank=True, null=True)),
                ('sentido', models.CharField(blank=True, choices=[('I', 'Ida'), ('V', 'Volta'), ('U', 'Unico')], default='I', max_length=3)),
                ('tipo', models.CharField(blank=True, choices=[('1', '1 Produtiva'), ('2', '2 Expresso'), ('3', '3 Semi Expresso'), ('4', '4 Extra'), ('5', '5 Acesso'), ('6', '6 Recolhe'), ('7', '7 Intervalo'), ('8', '8 T Turno'), ('9', '9 Reservado')], default='1', max_length=3)),
                ('dia_inicio', models.PositiveIntegerField(blank=True, default=1, null=True)),
                ('dia_fim', models.PositiveIntegerField(blank=True, default=1, null=True)),
                ('detalhe', models.CharField(blank=True, max_length=10)),
                ('carro', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trafego.carro')),
                ('destino', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='viagem_destino', to='trafego.localidade')),
                ('origem', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='viagem_origem', to='trafego.localidade')),
            ],
            options={
                'default_permissions': [],
            },
        ),
        migrations.CreateModel(
            name='Planejamento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo', models.CharField(max_length=15, unique=True)),
                ('descricao', models.CharField(blank=True, max_length=200)),
                ('dia_tipo', models.CharField(blank=True, choices=[('U', 'Util'), ('S', 'Sabado'), ('D', 'Domingo'), ('F', 'Ferias'), ('E', 'Especial')], default='U', max_length=3)),
                ('data_criacao', models.DateField(blank=True, default=datetime.datetime.today, null=True)),
                ('patamares', models.TextField(blank=True)),
                ('ativo', models.BooleanField(default=False)),
                ('pin', models.BooleanField(default=True)),
                ('empresa', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='core.empresa')),
                ('linha', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='trafego.linha')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Patamar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inicial', models.PositiveIntegerField()),
                ('final', models.PositiveIntegerField()),
                ('ida', models.PositiveIntegerField(blank=True, null=True)),
                ('volta', models.PositiveIntegerField(blank=True, null=True)),
                ('linha', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trafego.linha')),
            ],
            options={
                'default_permissions': ['change'],
            },
        ),
        migrations.CreateModel(
            name='Ocorrencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.DateField(blank=True, default=datetime.datetime.today, null=True)),
                ('hora', models.TimeField(blank=True, null=True)),
                ('indisciplina_condutor', models.BooleanField(default=False)),
                ('gravidade', models.CharField(blank=True, choices=[('L', 'Leve'), ('M', 'Medio'), ('G', 'Grave')], default='L', max_length=2)),
                ('viagem_omitida', models.BooleanField(default=False)),
                ('tratado', models.BooleanField(default=False)),
                ('detalhe', models.TextField(blank=True)),
                ('condutor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='pessoal.funcionario')),
                ('empresa', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='core.empresa')),
                ('evento', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='trafego.evento')),
                ('linha', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='trafego.linha')),
                ('local', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='trafego.localidade')),
                ('providencia', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='trafego.providencia')),
                ('usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
                ('veiculo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='oficina.frota')),
            ],
            options={
                'permissions': [('dashboard_ocorrencia', 'Pode ver dashboard ocorrencia'), ('tratar_ocorrencia', 'Pode tratar ocorrencia')],
            },
        ),
        migrations.CreateModel(
            name='Notificacao',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(blank=True, choices=[('N', 'Notificacao'), ('G', 'Multa Gestor'), ('T', 'Multa Transito')], default='N', max_length=2)),
                ('codigo', models.CharField(max_length=40, unique=True)),
                ('data', models.DateField(default=datetime.datetime.today)),
                ('hora', models.TimeField(null=True)),
                ('valor', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('prazo', models.DateField(blank=True, null=True)),
                ('detalhe', models.CharField(blank=True, max_length=200)),
                ('tratativa', models.TextField(blank=True)),
                ('veiculo_lacrado', models.BooleanField(default=False)),
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
            model_name='linha',
            name='destino',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='local_destino', to='trafego.localidade'),
        ),
        migrations.AddField(
            model_name='linha',
            name='empresa',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='core.empresa'),
        ),
        migrations.AddField(
            model_name='linha',
            name='origem',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='local_origem', to='trafego.localidade'),
        ),
        migrations.CreateModel(
            name='FotoOcorrencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('foto', core.models.ImageField(upload_to='trafego/ocorrencias/%Y/%m/%d', validators=[trafego.validators.validate_file_extension])),
                ('ocorrencia', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trafego.ocorrencia')),
            ],
            options={
                'default_permissions': [('add', 'view', 'delete')],
            },
        ),
        migrations.AddField(
            model_name='carro',
            name='planejamento',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trafego.planejamento'),
        ),
        migrations.AddField(
            model_name='agente',
            name='orgao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='trafego.orgao'),
        ),
    ]
