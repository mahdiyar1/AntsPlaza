# Generated by Django 4.0.7 on 2022-08-17 20:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('engine', '0029_symbol_kline_open_1_min'),
    ]

    operations = [
        migrations.DeleteModel(
            name='MarginBalance',
        ),
    ]
