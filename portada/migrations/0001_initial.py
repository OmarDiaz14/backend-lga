# Generated by Django 5.1 on 2024-10-22 18:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('catalogo', '0001_initial'),
        ('cuadro', '0001_initial'),
        ('ficha_tecnica', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='portada',
            fields=[
                ('id_expediente', models.AutoField(primary_key=True, serialize=False)),
                ('num_expediente', models.CharField(max_length=150)),
                ('asunto', models.CharField(max_length=150)),
                ('num_legajos', models.PositiveBigIntegerField(default=0)),
                ('num_fojas', models.PositiveBigIntegerField(default=0)),
                ('valores_secundarios', models.CharField(choices=[('informativo', 'Informativo'), ('evidencial', 'Evidencia'), ('testimonial', 'Testimonial')], default='informativo', max_length=15)),
                ('fecha_apertura', models.DateField()),
                ('fecha_cierre', models.DateField(null=True)),
                ('catalogo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='catalogo.catalogo')),
                ('ficha', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ficha_tecnica.fichatecnica')),
                ('seccion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cuadro.seccion')),
                ('serie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cuadro.series')),
                ('subserie', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cuadro.subserie')),
            ],
        ),
    ]
