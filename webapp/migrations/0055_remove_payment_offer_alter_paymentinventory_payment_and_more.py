# Generated by Django 5.1 on 2024-12-10 17:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0054_offer_alter_paymentinventory_payment_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='offer',
        ),
        migrations.AlterField(
            model_name='paymentinventory',
            name='payment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.payment'),
        ),
        migrations.AlterField(
            model_name='paymentservice',
            name='payment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.payment'),
        ),
        migrations.DeleteModel(
            name='Offer',
        ),
    ]