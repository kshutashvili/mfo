# Generated by Django 2.0.2 on 2018-08-13 12:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('payment_gateways', '0002_privatbankpayment'),
    ]

    operations = [
        migrations.AddField(
            model_name='privatbankpayment',
            name='save_dt',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Дата сохранения'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='privatbankpayment',
            name='confirm_dt',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата подтверждения транзакции'),
        ),
    ]
