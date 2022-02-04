# Generated by Django 3.2.3 on 2022-02-04 19:27

from django.db import migrations, models
import trafego.validators


class Migration(migrations.Migration):

    dependencies = [
        ('trafego', '0004_auto_20220204_1400'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fotoocorrencia',
            name='foto',
            field=models.ImageField(upload_to='trafego/ocorrencias/%Y/%m/%d', validators=[trafego.validators.validate_file_extension]),
        ),
    ]