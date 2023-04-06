# Generated by Django 4.2 on 2023-04-06 15:51

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Currency Name')),
            ],
            options={
                'verbose_name': 'валюта',
                'verbose_name_plural': 'валюты',
            },
        ),
        migrations.CreateModel(
            name='CurrencyProvider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, verbose_name='Network Name')),
            ],
            options={
                'verbose_name': 'Сеть проведения',
                'verbose_name_plural': 'Сети проведения',
            },
        ),
        migrations.CreateModel(
            name='rate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source', models.CharField(max_length=255, verbose_name='source of rate')),
                ('raw_data', models.TextField(blank=True, default='{}')),
                ('rate', models.DecimalField(decimal_places=20, max_digits=40, max_length=255, verbose_name='rate')),
                ('edit_user', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='user_provided_rate', to=settings.AUTH_USER_MODEL, verbose_name='Опертор')),
                ('give_currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='currency_provided1', to='exchange.currency', verbose_name='Give Currency')),
                ('take_currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='currency_provided2', to='exchange.currency', verbose_name='Take currency')),
            ],
        ),
        migrations.CreateModel(
            name='Orders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('created', 'создана'), ('processing', 'в процессе'), ('wait_secure', 'проверяется'), ('user_canceled', 'отменена клиентом'), ('canceled', 'отменена оператором'), ('processed', 'проведена'), ('failed', 'неуспешна')], default='created', max_length=40, verbose_name='Статус')),
                ('pub_date', models.DateTimeField(default=datetime.datetime.now, verbose_name='Дата публикации')),
                ('expire_date', models.DateTimeField(blank=True, null=True, verbose_name='Дата валидности')),
                ('amnt_give', models.DecimalField(decimal_places=20, max_digits=40, max_length=255, verbose_name='amnt give')),
                ('amnt_take', models.DecimalField(decimal_places=10, max_digits=40, max_length=255, verbose_name='amnt take')),
                ('rate', models.DecimalField(decimal_places=10, max_digits=40, max_length=255, verbose_name='exchange rate')),
                ('give_currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='give_currency', to='exchange.currency', verbose_name='Give Currency')),
                ('operator', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='user_open', to=settings.AUTH_USER_MODEL, verbose_name='Опертор')),
                ('provider_give', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='povider_give', to='exchange.currencyprovider', verbose_name='Provider Give Currency')),
                ('provider_take', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='provider_take', to='exchange.currencyprovider', verbose_name='Provider take Currency')),
                ('take_currency', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='take_currency', to='exchange.currency', verbose_name='Take currency')),
                ('user', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='user_p2p_suggester', to=settings.AUTH_USER_MODEL, verbose_name='Клиент')),
            ],
            options={
                'verbose_name': 'заявка на обмен',
                'verbose_name_plural': 'заявки на обмен',
            },
        ),
    ]
