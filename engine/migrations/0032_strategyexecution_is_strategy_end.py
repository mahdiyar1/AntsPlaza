# Generated by Django 4.0.7 on 2022-08-17 20:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0031_strategyexecution_long_buy_cost_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='strategyexecution',
            name='is_strategy_end',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]
