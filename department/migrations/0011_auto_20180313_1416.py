# Generated by Django 2.0.2 on 2018-03-13 12:16

from django.db import migrations
import django_google_maps.fields


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0010_department_address_ua'),
    ]

    operations = [
        migrations.AlterField(
            model_name='department',
            name='address',
            field=django_google_maps.fields.AddressField(max_length=128, verbose_name='Адрес [ru]'),
        ),
    ]
