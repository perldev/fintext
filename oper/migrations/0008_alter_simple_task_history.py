# Generated by Django 4.2 on 2023-06-01 13:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oper', '0007_simple_task'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simple_task',
            name='history',
            field=models.TextField(default=''),
        ),
    ]