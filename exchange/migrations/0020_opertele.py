# Generated by Django 4.2 on 2023-05-01 12:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('exchange', '0019_trans_debet_credit'),
    ]

    operations = [
        migrations.CreateModel(
            name='OperTele',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tele_link', models.CharField(max_length=255, verbose_name='telegram temp link')),
                ('tele_id', models.IntegerField(verbose_name='telegram id')),
                ('tele_username', models.CharField(default='', max_length=40, verbose_name='')),
                ('user', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='user_tele_suggester', to=settings.AUTH_USER_MODEL, verbose_name='Клиент')),
            ],
        ),
    ]
