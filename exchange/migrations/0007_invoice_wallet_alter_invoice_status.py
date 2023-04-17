# Generated by Django 4.2 on 2023-04-17 13:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0006_alter_invoice_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='wallet',
            field=models.CharField(choices=[('btc', '1231290o3dqwjlsanq0n'), ('eth', 'mgklf9304jhmvlfg8jmrtm')], default='btc', max_length=300, verbose_name='номер кошелька'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='status',
            field=models.CharField(choices=[('created', 'выставлен'), ('paid', 'оплачен'), ('canceled', 'отменен')], default='created', max_length=40, verbose_name='Статус'),
        ),
    ]
