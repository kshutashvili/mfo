# Generated by Django 2.0.2 on 2018-11-15 12:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0027_requestpersonalarea_message_sid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='requestpersonalarea',
            name='turnes_person_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID клиента в БД Turnes'),
        ),
    ]