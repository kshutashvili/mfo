# Generated by Django 2.0.2 on 2018-08-31 11:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0026_requestpersonalarea_has_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestpersonalarea',
            name='message_sid',
            field=models.CharField(blank=True, max_length=64, verbose_name='Twillio message SID'),
        ),
    ]
