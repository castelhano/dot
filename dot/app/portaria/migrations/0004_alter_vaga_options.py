# Generated by Django 4.2.4 on 2023-08-14 19:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('portaria', '0003_alter_veiculo_placa'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='vaga',
            options={'permissions': [('view_registro', 'Visualizar registro'), ('add_registro', 'Adicionar registro'), ('change_registro', 'Atualizar registro'), ('delete_registro', 'Excluir registro')]},
        ),
    ]
