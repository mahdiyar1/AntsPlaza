# Generated by Django 4.0.7 on 2022-08-16 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0023_alter_strategy_last_strategy_execution_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='strategy',
            old_name='last_strategy_execution_id',
            new_name='last_strategy_execution',
        ),
    ]
