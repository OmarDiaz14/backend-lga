# Generated by Django 5.1 on 2025-01-09 02:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cuadro', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='destino_expe',
            fields=[
                ('id_destino', models.AutoField(primary_key=True, serialize=False)),
                ('destino', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='type_access',
            fields=[
                ('id_type', models.AutoField(primary_key=True, serialize=False)),
                ('type', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='valores_docu',
            fields=[
                ('id_valores', models.AutoField(primary_key=True, serialize=False)),
                ('valores', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Catalogo',
            fields=[
                ('id_catalogo', models.AutoField(primary_key=True, serialize=False)),
                ('catalogo', models.CharField(max_length=50)),
                ('archivo_tramite', models.CharField(max_length=50)),
                ('archivo_concentracion', models.CharField(max_length=50)),
                ('observaciones', models.CharField(blank=True, db_column='observaciones ', max_length=250, null=True)),
                ('seccion', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cuadro.seccion')),
                ('serie', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='cuadro.series')),
                ('subserie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cuadro.subserie')),
                ('destino_expe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogo.destino_expe')),
                ('type_access', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalogo.type_access')),
                ('valores_documentales', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='catalogo.valores_docu')),
            ],
        ),
    ]
