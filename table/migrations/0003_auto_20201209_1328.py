# Generated by Django 3.1.4 on 2020-12-09 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('table', '0002_portfolio_cash'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stocktransactrecord',
            old_name='quantity',
            new_name='buy_quantity',
        ),
        migrations.RemoveField(
            model_name='portfolio',
            name='current_value',
        ),
        migrations.RemoveField(
            model_name='portfolio',
            name='percent_change',
        ),
        migrations.AddField(
            model_name='portfolio',
            name='description',
            field=models.CharField(default='', max_length=1000),
        ),
        migrations.AddField(
            model_name='stocktransactrecord',
            name='sell_quantity',
            field=models.PositiveIntegerField(blank=True, default=0),
        ),
    ]