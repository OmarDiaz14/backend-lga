# Generated by Django 5.1 on 2025-01-09 02:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('portada', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GuiaDocu',
            fields=[
                ('id_guia', models.AutoField(primary_key=True, serialize=False)),
                ('descripcion', models.CharField(blank=True, max_length=100, null=True)),
                ('volumen', models.IntegerField()),
                ('ubicacion_fisica', models.CharField(max_length=100)),
                ('num_expediente', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='portada.portada')),
            ],
        ),
    ]
