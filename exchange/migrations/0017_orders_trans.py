# Generated by Django 4.2 on 2023-04-24 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0016_remove_invoice_fiat_payments_details_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='trans',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='user_open', to='exchange.trans', verbose_name='транзакция выплаты'),
        ),
    ]