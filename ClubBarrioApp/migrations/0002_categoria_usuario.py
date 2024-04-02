# Generated by Django 5.0.3 on 2024-04-02 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ClubBarrioApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='categoria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=250)),
                ('apellidos', models.CharField(max_length=250)),
                ('password', models.CharField(max_length=250)),
                ('email', models.EmailField(max_length=250)),
            ],
        ),
    ]
