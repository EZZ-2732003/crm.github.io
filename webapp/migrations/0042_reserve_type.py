# Generated by Django 5.1 on 2024-12-04 14:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0041_payment_branch'),
    ]

    operations = [
        migrations.AddField(
            model_name='reserve',
            name='type',
            field=models.CharField(choices=[('old', 'old'), ('new', 'new')], default='old or new', max_length=100),
        ),
    ]