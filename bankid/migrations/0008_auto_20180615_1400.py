# Generated by Django 2.0.2 on 2018-06-15 11:00

import bankid.fields
import bankid.models
import bankid.storages
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bankid', '0007_auto_20180615_1224'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scandocument',
            name='file',
            field=bankid.fields.ProtectedFileField(blank=True, null=True, storage=bankid.storages.ProtectedFileSystemStorage(), upload_to=bankid.models.get_user_image_folder, verbose_name='Файл скана'),
        ),
    ]
