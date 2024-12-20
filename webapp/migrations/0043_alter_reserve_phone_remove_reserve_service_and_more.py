# Generated by Django 5.1 on 2024-12-04 14:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0042_reserve_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reserve',
            name='phone',
            field=models.CharField(max_length=100),
        ),
        migrations.RemoveField(
            model_name='reserve',
            name='service',
        ),
        migrations.AddField(
            model_name='reserve',
            name='service',
            field=models.ManyToManyField(related_name='reserves', to='webapp.service'),
        ),
    ]
