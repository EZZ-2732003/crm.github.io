# Generated by Django 5.1 on 2024-09-13 08:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0011_medical_history'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reserve',
            name='name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webapp.patient'),
        ),
    ]