# Generated by Django 2.0.2 on 2018-03-14 14:19

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0055_auto_20180314_1616'),
    ]

    operations = [
        migrations.AddField(
            model_name='mainpagestatic',
            name='copyright_ru',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Копирайт в футере [ru]'),
        ),
        migrations.AddField(
            model_name='mainpagestatic',
            name='copyright_ua',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Копирайт в футере [ua]'),
        ),
    ]
