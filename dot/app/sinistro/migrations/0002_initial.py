# Generated by Django 3.2.3 on 2022-02-18 13:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('trafego', '0001_initial'),
        ('oficina', '0001_initial'),
        ('sinistro', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='acidente',
            name='linha',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='trafego.linha'),
        ),
        migrations.AddField(
            model_name='acidente',
            name='veiculo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='oficina.frota'),
        ),
    ]