# Generated by Django 2.0.2 on 2018-05-04 08:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20180504_0943'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='turnes_person_id',
            field=models.CharField(blank=True, max_length=32, verbose_name='ID клиента в БД Turnes'),
        ),
    ]
