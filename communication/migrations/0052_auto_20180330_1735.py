# Generated by Django 2.0.2 on 2018-03-30 14:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0051_auto_20180330_1615'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userquestion',
            name='is_read',
            field=models.CharField(default='read', max_length=10, verbose_name='Прочитан'),
        ),
    ]