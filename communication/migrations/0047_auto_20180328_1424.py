# Generated by Django 2.0.2 on 2018-03-28 11:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0046_auto_20180328_0047'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='questioncomment',
            options={'ordering': ['created_at'], 'verbose_name': 'Комментарий к вопросу пользователя', 'verbose_name_plural': 'Комментарии к вопросам пользователя'},
        ),
    ]
