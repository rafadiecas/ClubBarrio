# Generated by Django 4.2.11 on 2024-05-06 17:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ClubBarrioApp', '0013_entrenamiento_equipo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producto',
            name='pedidos',
        ),
        migrations.RemoveField(
            model_name='producto',
            name='stock',
        ),
        migrations.RemoveField(
            model_name='producto',
            name='talla',
        ),
        migrations.AddField(
            model_name='producto',
            name='descripcion',
            field=models.TextField(default='sin descripción'),
        ),
        migrations.CreateModel(
            name='ProductoTalla',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stock', models.IntegerField(default=0)),
                ('pedidos', models.ManyToManyField(to='ClubBarrioApp.pedido')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ClubBarrioApp.producto')),
                ('talla', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='ClubBarrioApp.talla')),
            ],
        ),
        migrations.AddField(
            model_name='producto',
            name='tallas',
            field=models.ManyToManyField(through='ClubBarrioApp.ProductoTalla', to='ClubBarrioApp.talla'),
        ),
    ]
