# Generated by Django 2.0.2 on 2018-04-27 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_auto_20180427_1113'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='is_paid',
            field=models.BooleanField(default=False, verbose_name='Оплачен?'),
        ),
    ]
