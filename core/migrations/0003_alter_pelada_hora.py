# Generated by Django 5.1.6 on 2025-04-06 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_pelada_hora'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pelada',
            name='hora',
            field=models.TimeField(default='18:00:00'),
        ),
    ]
