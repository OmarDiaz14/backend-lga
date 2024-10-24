# Generated by Django 5.1 on 2024-10-22 18:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cuadro', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FichaTecnica',
            fields=[
                ('id_ficha', models.CharField(max_length=150, primary_key=True, serialize=False)),
                ('area_resguardante', models.CharField(max_length=250)),
                ('area_intervienen', models.CharField(max_length=250)),
                ('descripcion', models.CharField(max_length=250)),
                ('soporte_docu', models.CharField(max_length=250)),
                ('id_seccion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cuadro.seccion')),
                ('id_serie', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cuadro.series')),
                ('id_subserie', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cuadro.subserie')),
            ],
        ),
    ]
