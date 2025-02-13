# Generated by Django 5.1 on 2024-09-22 03:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0026_payment'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='inventory',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='inventory_quantity',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='inventory_total',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='service',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='service_quantity',
        ),
        migrations.RemoveField(
            model_name='payment',
            name='service_total',
        ),
        migrations.CreateModel(
            name='PaymentInventory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('inventory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.inventory')),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.payment')),
            ],
        ),
        migrations.CreateModel(
            name='PaymentService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('payment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.payment')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.service')),
            ],
        ),
    ]
