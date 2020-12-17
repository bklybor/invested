# Generated by Django 3.1.4 on 2020-12-14 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('table', '0008_cashtransactionrecord'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashtransactionrecord',
            name='currency_type',
            field=models.CharField(blank=True, choices=[('USD', 'United States Dollar'), ('EUR', 'European Euro'), ('GBP', 'British Pound'), ('JPY', 'Japanese Yen'), ('CAD', 'Canadian Dollar'), ('CHF', 'Swiss Franc')], default='USD', max_length=10),
        ),
        migrations.AlterField(
            model_name='cashtransactionrecord',
            name='transaction_type',
            field=models.CharField(blank=True, choices=[('deposit', 'Cash deposit in to the associated Portfolio.'), ('withdrawal', 'Cash withdrawal from the associated Portfolio.')], default='deposit', max_length=20),
        ),
    ]