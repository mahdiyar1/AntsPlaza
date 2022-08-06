# Generated by Django 4.0.6 on 2022-08-05 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0015_strategyexecution_leverage'),
    ]

    operations = [
        migrations.AddField(
            model_name='strategyexecution',
            name='last_long_return',
            field=models.DecimalField(decimal_places=12, max_digits=24, null=True),
        ),
        migrations.AddField(
            model_name='strategyexecution',
            name='last_short_return',
            field=models.DecimalField(decimal_places=12, max_digits=24, null=True),
        ),
    ]