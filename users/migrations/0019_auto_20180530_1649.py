# Generated by Django 2.0.2 on 2018-05-30 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0018_auto_20180530_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionnaire',
            name='education',
            field=models.TextField(blank=True, verbose_name='Освіта'),
        ),
    ]
