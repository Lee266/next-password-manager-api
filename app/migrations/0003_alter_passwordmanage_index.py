# Generated by Django 3.2.10 on 2023-05-28 11:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20230528_2024'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordmanage',
            name='index',
            field=models.PositiveIntegerField(),
        ),
    ]
