# Generated by Django 2.0.2 on 2018-03-17 23:09

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vacancy', '0008_auto_20180313_1609'),
        ('communication', '0028_delete_agreement'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resume',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=128, verbose_name='Имя')),
                ('last_name', models.CharField(max_length=128, verbose_name='Фамилия')),
                ('city', models.CharField(max_length=128, verbose_name='Населенный пункт')),
                ('phone', models.CharField(max_length=32, validators=[django.core.validators.RegexValidator(message='Неправильный формат телефона: ', regex='^\\+{0,1}\\d{9,15}$')], verbose_name='Номер телефона')),
                ('email', models.EmailField(max_length=254, verbose_name='Электронная почта')),
                ('file', models.FileField(upload_to='resume_files', verbose_name='Резюме')),
                ('vacancy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vacancy.Vacancy', verbose_name='Вакансия')),
            ],
            options={
                'verbose_name': 'Резюме',
                'verbose_name_plural': 'Резюме',
            },
        ),
    ]