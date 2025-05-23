# Generated by Django 5.1 on 2024-12-18 04:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0057_remove_companies_total_due_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='installments_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='invoice',
            name='remaining_amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='payment_method',
            field=models.CharField(choices=[('Cash', 'Cash Payment'), ('Installments', 'Installment Payment')], default='Cash', max_length=15),
        ),
    ]
