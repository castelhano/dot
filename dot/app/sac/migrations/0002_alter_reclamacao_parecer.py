# Generated by Django 3.2.3 on 2022-06-09 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sac', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reclamacao',
            name='parecer',
            field=models.CharField(choices=[('', 'Em analise'), ('P', 'Procedente'), ('I', 'Improcedente')], default='', max_length=5),
        ),
    ]
