# Generated by Django 5.1 on 2024-12-06 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ficha_tecnica', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fichatecnica',
            name='topologia',
            field=models.CharField(default=1, max_length=250),
            preserve_default=False,
        ),
    ]