# Generated by Django 4.0.2 on 2022-02-20 14:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sinistro', '0003_alter_terceiro_acidente'),
    ]

    operations = [
        migrations.AlterField(
            model_name='terceiro',
            name='acidente',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='sinistro.acidente'),
        ),
    ]
