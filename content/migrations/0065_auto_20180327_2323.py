# Generated by Django 2.0.2 on 2018-03-27 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0064_auto_20180325_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='discountstatic',
            name='image',
            field=models.FileField(null=True, upload_to='discount_icons', verbose_name='Иконки'),
        ),
    ]
