# Generated by Django 3.1.4 on 2020-12-15 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StockManagementSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('internal_value_threshold', models.DecimalField(decimal_places=6, default=100000, help_text='Amount in USD at which to halt processing of an internal stock order.', max_digits=18)),
                ('external_value_threshold', models.DecimalField(decimal_places=6, default=1000000, help_text='Amount in USD at which to halt processing of an external stock order.', max_digits=18)),
                ('internal_share_proportion_threshold', models.DecimalField(decimal_places=6, default=0.1, help_text='Fraction of order shares over internally held shares at which to halt processing of an internal stock order.', max_digits=18)),
                ('external_share_proportion_threshold', models.DecimalField(decimal_places=6, default=0.1, help_text='Fraction of order shares over externally held shares at which to halt processing of an external stock order', max_digits=18)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
