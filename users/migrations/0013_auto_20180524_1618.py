# Generated by Django 2.0.2 on 2018-05-24 13:18

from django.db import migrations, models
import django.utils.timezone
import users.validators


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_auto_20180524_1155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionnaire',
            name='birthday_date',
            field=models.DateField(blank=True, default=django.utils.timezone.now, verbose_name='Дата народження'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='email',
            field=models.EmailField(max_length=254, verbose_name='Email адрес'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='first_name',
            field=models.CharField(max_length=128, verbose_name="Ім'я"),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='itn',
            field=models.CharField(max_length=10, verbose_name='ІПН'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='last_name',
            field=models.CharField(max_length=128, verbose_name='Прізвище'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='middle_name',
            field=models.CharField(max_length=128, verbose_name='По батькові'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='mobile_phone',
            field=models.CharField(max_length=30, validators=[users.validators.mobile_phone_number], verbose_name='Контактний телефон'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='passport_authority',
            field=models.CharField(max_length=128, verbose_name='Орган, що видав'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='passport_code',
            field=models.CharField(max_length=9, verbose_name='Серія та номер паспорта / Номер ID-картки'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='passport_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='Дата видачі паспорта'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='registration_building',
            field=models.TextField(verbose_name='№ Будинку'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='registration_city',
            field=models.TextField(verbose_name='Місто (СМТ, село)'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='registration_country',
            field=models.TextField(verbose_name='Країна'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='registration_flat',
            field=models.TextField(verbose_name='№ Квартири'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='registration_state',
            field=models.TextField(verbose_name='Область (Регіон)'),
        ),
        migrations.AlterField(
            model_name='questionnaire',
            name='registration_street',
            field=models.TextField(verbose_name='Вулиця (проспект, бульвар тощо)'),
        ),
    ]
