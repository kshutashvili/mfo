# Generated by Django 2.0.2 on 2018-03-27 18:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0035_questioncomments_userquestion'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='QuestionComments',
            new_name='QuestionComment',
        ),
    ]
