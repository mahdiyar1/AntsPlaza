# Generated by Django 4.0.7 on 2022-08-26 00:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0040_alter_strategyexecution_task_id'),
    ]

    operations = [
        migrations.RenameField(
            model_name='strategyexecution',
            old_name='task_id',
            new_name='task',
        ),
    ]
