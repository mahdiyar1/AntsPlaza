# Generated by Django 4.0.7 on 2022-08-16 12:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0021_remove_strategy_last_strategy_execution_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='strategy',
            name='last_strategy_execution_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='last_strategy_execution_id', to='engine.strategyexecution'),
            preserve_default=False,
        ),
    ]
