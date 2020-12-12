# Generated by Django 3.1.4 on 2020-12-09 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('table', '0004_auto_20201209_1438'),
    ]

    operations = [
        migrations.RenameField(
            model_name='stock',
            old_name='date_retrieved',
            new_name='date',
        ),
        migrations.AlterField(
            model_name='portfolio',
            name='cash',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=20),
        ),
        migrations.AlterField(
            model_name='stock',
            name='price',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=50),
        ),
        migrations.AlterField(
            model_name='stocktransactrecord',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=6, default=0, max_digits=50),
        ),
        migrations.AlterUniqueTogether(
            name='stock',
            unique_together={('ticker', 'date')},
        ),
    ]