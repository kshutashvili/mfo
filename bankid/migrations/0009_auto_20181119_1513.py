# Generated by Django 2.0.2 on 2018-11-19 13:13

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bankid', '0008_auto_20180615_1400'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='created_dt',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='address',
            name='updated_dt',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.AddField(
            model_name='customer',
            name='created_dt',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='customer',
            name='updated_dt',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.AddField(
            model_name='document',
            name='created_dt',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='document',
            name='updated_dt',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
        migrations.AddField(
            model_name='scandocument',
            name='created_dt',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='scandocument',
            name='updated_dt',
            field=models.DateTimeField(auto_now=True, verbose_name='Дата обновления'),
        ),
    ]