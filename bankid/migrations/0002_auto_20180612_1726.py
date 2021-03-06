# Generated by Django 2.0.2 on 2018-06-12 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bankid', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='address',
            name='area',
            field=models.TextField(blank=True, verbose_name='Район'),
        ),
        migrations.AddField(
            model_name='address',
            name='flat_no',
            field=models.TextField(blank=True, verbose_name='Номер квартиры'),
        ),
        migrations.AddField(
            model_name='address',
            name='house_no',
            field=models.TextField(blank=True, verbose_name='Номер дома'),
        ),
        migrations.AlterField(
            model_name='address',
            name='type',
            field=models.TextField(blank=True, help_text='factual — адрес регистрации\nbirth – адрес рождения', verbose_name='Тип адреса'),
        ),
    ]
