# Generated by Django 3.1.5 on 2021-01-21 02:15

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CashManagementSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_one_deposit_max', models.DecimalField(decimal_places=6, default=10000, help_text='Maximum amount in USD that a client can deposit into a portfolio at one time.', max_digits=18)),
                ('client_one_deposit_min', models.DecimalField(decimal_places=6, default=100, help_text='Minimum amount in USD that a client can deposit into a portfolio at one time.', max_digits=18)),
                ('client_total_deposit_max', models.DecimalField(decimal_places=6, default=1000000, help_text='Maximum amount in USD that a client can have in a portfolio.', max_digits=18)),
                ('client_total_deposit_min', models.DecimalField(decimal_places=6, default=1000, help_text='Minimum amount in USD that a client can have in a portfolio.', max_digits=18)),
                ('client_withdrawal_max', models.DecimalField(decimal_places=6, default=10000, help_text='Maximum amount in USD that a client can freely withdraw from a portfolio.', max_digits=18)),
                ('client_withdrawal_time_period', models.DecimalField(decimal_places=6, default=1, help_text="Time period in days (24 hour days) over which to calculate the total amount  of withdrawals from a client's portfolio. The idea is that a client cannot freely withdraw more than the client_withdrawal_maximum within this time period without triggering a review by a broker.", max_digits=18)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('db_default_date', models.DateTimeField(default=datetime.datetime(1, 1, 1, 0, 0, tzinfo=utc))),
                ('monetary_decimal_places', models.PositiveIntegerField(default=6)),
                ('db_date_format', models.CharField(default='%Y-%m-%d %H:%M:%S', max_length=20)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StockManagementSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('internal_value_threshold', models.DecimalField(decimal_places=6, default=100000, help_text='Amount in USD at which to halt processing of an internal stock order.', max_digits=18)),
                ('external_value_threshold', models.DecimalField(decimal_places=6, default=1000000, help_text='Amount in USD at which to halt processing of an external stock order.', max_digits=18)),
                ('internal_share_proportion_threshold', models.DecimalField(decimal_places=6, default=0.1, help_text='Fraction of order shares over internally held shares at which to halt processing of an internal stock order.', max_digits=18)),
                ('external_share_proportion_threshold', models.DecimalField(decimal_places=6, default=0.1, help_text='Fraction of order shares over externally held shares at which to halt processing of an external stock order', max_digits=18)),
                ('internal_short_share_threshold', models.IntegerField(default=1000, help_text='The maximum allowable share deficit.')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
