# Generated by Django 4.1.5 on 2023-01-14 04:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_user_is_staff'),
    ]

    operations = [
        migrations.CreateModel(
            name='PasswordManage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(blank=True, max_length=255)),
                ('password', models.TextField()),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('created_at', models.DateField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
