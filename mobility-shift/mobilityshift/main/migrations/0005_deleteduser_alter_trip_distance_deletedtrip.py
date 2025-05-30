# Generated by Django 5.2 on 2025-04-23 07:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_alter_trip_text_response'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeletedUser',
            fields=[
                ('uuid', models.UUIDField(editable=False, primary_key=True, serialize=False)),
                ('sign_up_time', models.DateTimeField(editable=False)),
                ('age_group', models.CharField(choices=[('<13', 'Less than 13'), ('13-17', '13 - 17'), ('18-24', '18 - 24'), ('25-34', '25 - 34'), ('35-44', '35 - 44'), ('45-64', '45 - 64'), ('>65', 'More than 65'), ('prefer_not', 'Prefer not to say')], help_text='Select your age group')),
                ('gender', models.CharField(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ('prefer_not', 'Prefer not to say')], help_text='Select your gender')),
            ],
        ),
        migrations.AlterField(
            model_name='trip',
            name='distance',
            field=models.PositiveIntegerField(choices=[(0, '0km'), (500, '0.5km'), (1000, '1km'), (2500, '2.5km'), (5000, '5km'), (10000, '10km'), (25000, '25km'), (50000, '50km')]),
        ),
        migrations.CreateModel(
            name='DeletedTrip',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(blank=True, choices=[('walk', 'Walking'), ('bike', 'Cycling'), ('bus', 'Bussing')], null=True)),
                ('log_time', models.DateTimeField(editable=False)),
                ('distance', models.PositiveIntegerField(choices=[(0, '0km'), (500, '0.5km'), (1000, '1km'), (2500, '2.5km'), (5000, '5km'), (10000, '10km'), (25000, '25km'), (50000, '50km')])),
                ('text_response', models.TextField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.user')),
            ],
        ),
    ]
