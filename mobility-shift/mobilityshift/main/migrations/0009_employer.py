# Generated by Django 5.2 on 2025-05-17 08:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_remove_deleteduser_gender_remove_user_gender'),
    ]

    operations = [
        migrations.CreateModel(
            name='Employer',
            fields=[
                ('name', models.CharField(primary_key=True, serialize=False, unique=True)),
            ],
        ),
    ]
