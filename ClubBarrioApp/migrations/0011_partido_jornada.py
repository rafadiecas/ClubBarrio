# Generated by Django 4.2.11 on 2024-04-23 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ClubBarrioApp', '0010_alter_partido_puntos_equipo1_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='partido',
            name='jornada',
            field=models.IntegerField(default=0),
        ),
    ]
