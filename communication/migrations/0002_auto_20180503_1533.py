# Generated by Django 2.0.2 on 2018-05-03 12:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('communication', '0001_initial'),
        ('vacancy', '0001_initial'),
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userquestion',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='users.Profile', verbose_name='Пользователь'),
        ),
        migrations.AddField(
            model_name='userexistmessage',
            name='page',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='communication.SuccessFormStatic', verbose_name='Форма'),
        ),
        migrations.AddField(
            model_name='resume',
            name='vacancy',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='vacancy.Vacancy', verbose_name='Вакансия'),
        ),
        migrations.AddField(
            model_name='lastarticles',
            name='articles',
            field=models.ManyToManyField(to='communication.BlogItem', verbose_name='Статьи'),
        ),
        migrations.AddField(
            model_name='faqpagestatic',
            name='faq_categories',
            field=models.ManyToManyField(to='communication.FaqCategory', verbose_name='Категории с вопросами'),
        ),
        migrations.AddField(
            model_name='faqcategory',
            name='faq_items',
            field=models.ManyToManyField(to='communication.FaqItem'),
        ),
        migrations.AddField(
            model_name='contact',
            name='email',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='communication.Email', verbose_name='Электронная почта'),
        ),
        migrations.AddField(
            model_name='contact',
            name='phones',
            field=models.ManyToManyField(to='communication.PhoneNumber', verbose_name='Телефоны'),
        ),
        migrations.AddField(
            model_name='contact',
            name='success_form',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='communication.SuccessFormStatic', verbose_name='Форма при успешной отправке сообщения'),
        ),
        migrations.AddField(
            model_name='contact',
            name='to_email',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='to_email', to='communication.Email', verbose_name='Электронная почта для напишите нам'),
        ),
        migrations.AddField(
            model_name='callbacksuccessform',
            name='success',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='communication.SuccessFormStatic', verbose_name='Форма успешного заказа'),
        ),
        migrations.AddField(
            model_name='blogcategory',
            name='blog_items',
            field=models.ManyToManyField(to='communication.BlogItem', verbose_name='Статьи'),
        ),
    ]
