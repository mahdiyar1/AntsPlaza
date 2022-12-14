# Generated by Django 4.0.7 on 2022-08-28 23:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0042_strategyexecution_long_symbol_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='strategyexecution',
            name='long_symbol',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='execution_long_symbol', to='engine.symbol'),
        ),
        migrations.AlterField(
            model_name='strategyexecution',
            name='short_symbol',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='execution_short_symbol', to='engine.symbol'),
        ),
    ]
