# Generated by Django 2.0.2 on 2018-11-19 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0030_auto_20181116_1515'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionnaire',
            name='vehicle_count',
            field=models.IntegerField(default=0, verbose_name='Кількість автомобілів'),
        ),
    ]
