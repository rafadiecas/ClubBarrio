# Generated by Django 4.2.11 on 2024-05-27 23:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ClubBarrioApp', '0025_evento'),
    ]

    operations = [
        migrations.CreateModel(
            name='Valoraciones',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntuacion', models.IntegerField()),
                ('comentario', models.TextField(default='sin comentario')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ClubBarrioApp.producto')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]