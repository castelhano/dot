# Generated by Django 4.2.4 on 2023-08-16 14:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portaria', '0004_alter_vaga_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registrofuncionario',
            name='veiculo',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, to='portaria.veiculo'),
        ),
    ]
