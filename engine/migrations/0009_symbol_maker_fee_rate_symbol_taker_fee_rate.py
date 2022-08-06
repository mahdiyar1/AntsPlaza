# Generated by Django 4.0.6 on 2022-08-04 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0008_order_cost_minus_fee'),
    ]

    operations = [
        migrations.AddField(
            model_name='symbol',
            name='maker_fee_rate',
            field=models.DecimalField(
                decimal_places=12, default=0.0001, max_digits=24),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='symbol',
            name='taker_fee_rate',
            field=models.DecimalField(
                decimal_places=12, default=0.0001, max_digits=24),
            preserve_default=False,
        ),
    ]
