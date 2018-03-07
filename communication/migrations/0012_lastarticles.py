# Generated by Django 2.0.2 on 2018-03-06 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('communication', '0011_blogitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='LastArticles',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('articles', models.ManyToManyField(to='communication.BlogItem', verbose_name='Статьи')),
            ],
            options={
                'verbose_name_plural': 'Блок последние статьи',
                'verbose_name': 'Последние статьи',
            },
        ),
    ]