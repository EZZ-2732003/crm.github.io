# Generated by Django 5.1 on 2024-12-10 17:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0056_offers'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='companies',
            name='total_due',
        ),
        migrations.RemoveField(
            model_name='companies',
            name='total_paid',
        ),
        migrations.RemoveField(
            model_name='inventory',
            name='item_price',
        ),
    ]
