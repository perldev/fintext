# Generated by Django 4.2 on 2023-05-26 10:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0043_merge_20230526_0942'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orders',
            name='trans',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='exchange.trans', verbose_name='транзакция выплаты'),
        ),
    ]
