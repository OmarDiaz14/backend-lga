# Generated by Django 5.1 on 2025-01-09 02:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cuadro', '0001_initial'),
        ('portada', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventario',
            fields=[
                ('num_consecutivo', models.AutoField(primary_key=True, serialize=False)),
                ('descripcion', models.CharField(max_length=250, null=True)),
                ('observaciones', models.CharField(max_length=250, null=True)),
                ('expediente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='portada.portada')),
                ('serie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cuadro.series')),
            ],
        ),
    ]
