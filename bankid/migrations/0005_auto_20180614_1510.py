# Generated by Django 2.0.2 on 2018-06-14 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bankid', '0004_auto_20180612_1754'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scandocument',
            name='file',
            field=models.FileField(blank=True, null=True, upload_to='../protected_files', verbose_name='Файл скана'),
        ),
    ]
