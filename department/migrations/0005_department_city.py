# Generated by Django 2.0.2 on 2018-03-09 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('department', '0004_remove_department_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='department',
            name='city',
            field=models.CharField(max_length=128, null=True, verbose_name='Город'),
        ),
    ]
