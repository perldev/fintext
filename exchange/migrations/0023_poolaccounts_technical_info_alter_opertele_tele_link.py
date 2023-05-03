# Generated by Django 4.2 on 2023-05-03 13:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0022_alter_opertele_tele_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='poolaccounts',
            name='technical_info',
            field=models.CharField(default='', max_length=255, verbose_name='Техническая информация для обработки платежей'),
        ),
        migrations.AlterField(
            model_name='opertele',
            name='tele_link',
            field=models.CharField(max_length=255, verbose_name='telegram temp link'),
        ),
    ]
