# Generated by Django 4.2 on 2023-06-21 14:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oper', '0008_alter_simple_task_history'),
    ]

    operations = [
        migrations.AlterField(
            model_name='simple_task',
            name='command_name',
            field=models.CharField(max_length=255, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='simple_task',
            name='command_params',
            field=models.TextField(max_length=255, verbose_name='params'),
        ),
    ]
