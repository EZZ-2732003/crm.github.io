# Generated by Django 4.2.9 on 2025-01-26 09:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0080_alter_reserve_services'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reserve',
            name='services',
            field=models.JSONField(default=list),
        ),
    ]
