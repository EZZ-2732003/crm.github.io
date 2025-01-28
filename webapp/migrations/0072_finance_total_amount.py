# Generated by Django 5.1 on 2025-01-03 13:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0071_remove_finance_total_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='finance',
            name='total_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
    ]
