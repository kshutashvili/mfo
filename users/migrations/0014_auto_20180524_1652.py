# Generated by Django 2.0.2 on 2018-05-24 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0013_auto_20180524_1618'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionnaire',
            name='birthday_date',
            field=models.DateField(verbose_name='Дата народження'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='registration_country',
            field=models.TextField(blank=True, verbose_name='Країна'),
        ),
    ]