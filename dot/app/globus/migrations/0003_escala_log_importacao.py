# Generated by Django 4.0.2 on 2022-03-08 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('globus', '0002_alter_escala_empresa'),
    ]

    operations = [
        migrations.AddField(
            model_name='escala',
            name='log_importacao',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
