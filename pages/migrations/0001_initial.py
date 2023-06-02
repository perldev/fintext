# Generated by Django 4.2 on 2023-06-01 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangePage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_ru', models.CharField(max_length=255, verbose_name='заголовок ru')),
                ('title_uk', models.CharField(max_length=255, verbose_name='заголовок uk')),
                ('content_ru', models.TextField(blank=True, null=True, verbose_name='текст ru')),
                ('content_uk', models.TextField(blank=True, null=True, verbose_name='текст uk')),
                ('currency_from', models.CharField(max_length=20, verbose_name='валюта from')),
                ('currency_to', models.CharField(max_length=20, verbose_name='валюта to')),
                ('slug', models.CharField(blank=True, max_length=255, null=True, verbose_name='url страницы')),
            ],
            options={
                'verbose_name': 'Страница обмена',
                'verbose_name_plural': 'Страницы обмена',
            },
        ),
    ]
