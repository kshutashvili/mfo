# Generated by Django 2.0.2 on 2018-05-24 08:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0011_auto_20180523_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionnaire',
            name='itn',
            field=models.CharField(blank=True, max_length=10, verbose_name='ІПН'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]