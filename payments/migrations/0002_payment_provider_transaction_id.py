# Generated by Django 2.0.2 on 2018-04-25 12:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='provider_transaction_id',
            field=models.IntegerField(default=0, verbose_name='ID транзакции в системе 4bill'),
        ),
    ]
