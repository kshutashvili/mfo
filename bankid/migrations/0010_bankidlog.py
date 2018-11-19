# Generated by Django 2.0.2 on 2018-11-19 14:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bankid', '0009_auto_20181119_1513'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankIDLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=256, verbose_name='Тип')),
                ('subtype', models.CharField(blank=True, max_length=128, verbose_name='Подтип')),
                ('message', models.TextField(blank=True, verbose_name='Данные')),
                ('created_dt', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('updated_dt', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
            ],
            options={
                'verbose_name_plural': 'Логи (BankID)',
                'verbose_name': 'Логи (BankID)',
            },
        ),
    ]
