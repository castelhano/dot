# Generated by Django 4.0.2 on 2022-04-03 14:09

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gestao', '0002_alter_plano_staff'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plano',
            name='staff',
            field=models.ManyToManyField(related_name='plano_staff', to=settings.AUTH_USER_MODEL),
        ),
    ]
