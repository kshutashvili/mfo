# Generated by Django 2.0.2 on 2018-03-06 15:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0032_mainpagetopblockstatic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mainpagetopblockstatic',
            name='subtitle',
            field=models.CharField(max_length=128, verbose_name='Подзаголовок'),
        ),
    ]