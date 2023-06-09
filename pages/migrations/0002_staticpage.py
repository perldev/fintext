# Generated by Django 4.2 on 2023-06-01 17:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StaticPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title_ru', models.CharField(max_length=255, verbose_name='заголовок ru')),
                ('title_uk', models.CharField(max_length=255, verbose_name='заголовок uk')),
                ('content_ru', models.TextField(blank=True, null=True, verbose_name='текст ru')),
                ('content_uk', models.TextField(blank=True, null=True, verbose_name='текст uk')),
                ('slug', models.CharField(blank=True, max_length=255, null=True, verbose_name='url страницы')),
            ],
            options={
                'verbose_name': 'Статичная страница',
                'verbose_name_plural': 'Статичные страницы',
            },
        ),
    ]
