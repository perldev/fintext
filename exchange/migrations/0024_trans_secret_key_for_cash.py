# Generated by Django 4.2 on 2023-05-02 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exchange', '0023_alter_trans_account'),
    ]

    operations = [
        migrations.AddField(
            model_name='trans',
            name='secret_key_for_cash',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Код для получения наличных'),
        ),
    ]
