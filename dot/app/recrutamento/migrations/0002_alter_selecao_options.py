# Generated by Django 3.2.3 on 2022-02-04 14:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recrutamento', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='selecao',
            options={'permissions': [('dashboard_recrutamento', 'Pode acessar dashboard recrutamento')]},
        ),
    ]
