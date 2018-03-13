# Generated by Django 2.0.2 on 2018-03-12 20:30

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0049_remove_mainpagestatic_h1'),
    ]

    operations = [
        migrations.AddField(
            model_name='aboutusstatic',
            name='important_title_ru',
            field=models.CharField(max_length=128, null=True, verbose_name='Заголовок важных аспектов'),
        ),
        migrations.AddField(
            model_name='aboutusstatic',
            name='important_title_ua',
            field=models.CharField(max_length=128, null=True, verbose_name='Заголовок важных аспектов'),
        ),
        migrations.AddField(
            model_name='aboutusstatic',
            name='middle_text_ru',
            field=models.TextField(null=True, verbose_name='Текст на середине страницы'),
        ),
        migrations.AddField(
            model_name='aboutusstatic',
            name='middle_text_ua',
            field=models.TextField(null=True, verbose_name='Текст на середине страницы'),
        ),
        migrations.AddField(
            model_name='aboutusstatic',
            name='middle_title_ru',
            field=models.CharField(max_length=128, null=True, verbose_name='Заголовок на середине страницы'),
        ),
        migrations.AddField(
            model_name='aboutusstatic',
            name='middle_title_ua',
            field=models.CharField(max_length=128, null=True, verbose_name='Заголовок на середине страницы'),
        ),
        migrations.AddField(
            model_name='aboutusstatic',
            name='subtitle_ru',
            field=models.CharField(max_length=64, null=True, verbose_name='Подзаголовок'),
        ),
        migrations.AddField(
            model_name='aboutusstatic',
            name='subtitle_ua',
            field=models.CharField(max_length=64, null=True, verbose_name='Подзаголовок'),
        ),
        migrations.AddField(
            model_name='aboutusstatic',
            name='text_ru',
            field=models.TextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='aboutusstatic',
            name='text_ua',
            field=models.TextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='aboutusstatic',
            name='title_ru',
            field=models.CharField(max_length=64, null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='aboutusstatic',
            name='title_ua',
            field=models.CharField(max_length=64, null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='advantage',
            name='text_ru',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='advantage',
            name='text_ua',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='advantagestatic',
            name='text_ru',
            field=models.TextField(null=True, verbose_name='небольшой текст'),
        ),
        migrations.AddField(
            model_name='advantagestatic',
            name='text_ua',
            field=models.TextField(null=True, verbose_name='небольшой текст'),
        ),
        migrations.AddField(
            model_name='advantagestatic',
            name='title_ru',
            field=models.CharField(max_length=128, null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='advantagestatic',
            name='title_ua',
            field=models.CharField(max_length=128, null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='closecredit',
            name='text_ru',
            field=models.TextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='closecredit',
            name='text_ua',
            field=models.TextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='closecredit',
            name='title_ru',
            field=models.CharField(max_length=128, null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='closecredit',
            name='title_ua',
            field=models.CharField(max_length=128, null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='creditinformation',
            name='text_ru',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='creditinformation',
            name='text_ua',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='creditinformation',
            name='title_ru',
            field=models.CharField(max_length=128, null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='creditinformation',
            name='title_ua',
            field=models.CharField(max_length=128, null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='creditinformationblockstatic',
            name='text_ru',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='creditinformationblockstatic',
            name='text_ua',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='creditratestatic',
            name='text_ru',
            field=models.TextField(null=True, verbose_name='Небольшой текст'),
        ),
        migrations.AddField(
            model_name='creditratestatic',
            name='text_ua',
            field=models.TextField(null=True, verbose_name='Небольшой текст'),
        ),
        migrations.AddField(
            model_name='creditratestatic',
            name='title_ru',
            field=models.CharField(max_length=128, null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='creditratestatic',
            name='title_ua',
            field=models.CharField(max_length=128, null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='discountstatic',
            name='text_ru',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='discountstatic',
            name='text_ua',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='discountstatic',
            name='title_ru',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='discountstatic',
            name='title_ua',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='getcredit',
            name='text_ru',
            field=models.TextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='getcredit',
            name='text_ua',
            field=models.TextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='getcredit',
            name='title_ru',
            field=models.CharField(max_length=128, null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='getcredit',
            name='title_ua',
            field=models.CharField(max_length=128, null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='importantaspect',
            name='text_ru',
            field=models.TextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='importantaspect',
            name='text_ua',
            field=models.TextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='importantaspect',
            name='title_ru',
            field=models.CharField(max_length=64, null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='importantaspect',
            name='title_ua',
            field=models.CharField(max_length=64, null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='jobstaticpage',
            name='text_ru',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='jobstaticpage',
            name='text_ua',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='menuaboutitem',
            name='name_ru',
            field=models.CharField(max_length=128, null=True, verbose_name='Название пункта'),
        ),
        migrations.AddField(
            model_name='menuaboutitem',
            name='name_ua',
            field=models.CharField(max_length=128, null=True, verbose_name='Название пункта'),
        ),
        migrations.AddField(
            model_name='menufooterblock',
            name='name_ru',
            field=models.CharField(max_length=128, null=True, verbose_name='Название блока'),
        ),
        migrations.AddField(
            model_name='menufooterblock',
            name='name_ua',
            field=models.CharField(max_length=128, null=True, verbose_name='Название блока'),
        ),
        migrations.AddField(
            model_name='menufooteritem',
            name='name_ru',
            field=models.CharField(max_length=128, null=True, verbose_name='Название пункта'),
        ),
        migrations.AddField(
            model_name='menufooteritem',
            name='name_ua',
            field=models.CharField(max_length=128, null=True, verbose_name='Название пункта'),
        ),
        migrations.AddField(
            model_name='menuheaderitem',
            name='name_ru',
            field=models.CharField(max_length=128, null=True, verbose_name='Название пункта'),
        ),
        migrations.AddField(
            model_name='menuheaderitem',
            name='name_ua',
            field=models.CharField(max_length=128, null=True, verbose_name='Название пункта'),
        ),
        migrations.AddField(
            model_name='securityitem',
            name='text_ru',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='securityitem',
            name='text_ua',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Текст'),
        ),
        migrations.AddField(
            model_name='spoiler',
            name='content_left_ru',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Текст левой колонки'),
        ),
        migrations.AddField(
            model_name='spoiler',
            name='content_left_ua',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Текст левой колонки'),
        ),
        migrations.AddField(
            model_name='spoiler',
            name='content_right_ru',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Текст правой колонки'),
        ),
        migrations.AddField(
            model_name='spoiler',
            name='content_right_ua',
            field=ckeditor.fields.RichTextField(null=True, verbose_name='Текст правой колонки'),
        ),
        migrations.AddField(
            model_name='spoiler',
            name='topic_ru',
            field=models.CharField(max_length=64, null=True, verbose_name='Тема спойлера'),
        ),
        migrations.AddField(
            model_name='spoiler',
            name='topic_ua',
            field=models.CharField(max_length=64, null=True, verbose_name='Тема спойлера'),
        ),
        migrations.AddField(
            model_name='staticpage',
            name='title_ru',
            field=models.CharField(max_length=128, null=True, verbose_name='Заголовок'),
        ),
        migrations.AddField(
            model_name='staticpage',
            name='title_ua',
            field=models.CharField(max_length=128, null=True, verbose_name='Заголовок'),
        ),
    ]
