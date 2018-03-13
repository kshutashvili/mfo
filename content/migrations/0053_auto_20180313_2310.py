# Generated by Django 2.0.2 on 2018-03-13 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0052_auto_20180313_2254'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='menuaboutitem',
            options={'ordering': ['order'], 'verbose_name': 'Пункт меню', 'verbose_name_plural': 'Пункты меню на странице "О нас"'},
        ),
        migrations.AddField(
            model_name='menuaboutitem',
            name='order',
            field=models.PositiveIntegerField(default=0, verbose_name='Порядок'),
        ),
    ]
