# Generated by Django 5.1 on 2024-12-06 18:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0002_rename_id_subserie_catalogo_subserie'),
        ('ficha_tecnica', '0002_fichatecnica_topologia'),
    ]

    operations = [
        migrations.AddField(
            model_name='fichatecnica',
            name='catalogo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='catalogo.catalogo'),
        ),
    ]