# Generated by Django 2.0.2 on 2018-03-12 18:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0021_auto_20180312_2022'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogitem',
            name='text_ru',
        ),
        migrations.RemoveField(
            model_name='blogitem',
            name='title_ru',
        ),
    ]
