# Generated by Django 5.1 on 2024-12-30 04:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0067_rename_offer_name_offers_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='offer',
        ),
    ]
