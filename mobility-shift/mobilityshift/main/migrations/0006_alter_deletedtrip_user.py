# Generated by Django 5.2 on 2025-04-23 08:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_deleteduser_alter_trip_distance_deletedtrip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deletedtrip',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.deleteduser'),
        ),
    ]
