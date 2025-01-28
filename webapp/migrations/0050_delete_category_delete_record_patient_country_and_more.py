# Generated by Django 5.1 on 2024-12-08 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0049_alter_patient_phone'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Category',
        ),
        migrations.DeleteModel(
            name='Record',
        ),
        migrations.AddField(
            model_name='patient',
            name='country',
            field=models.CharField(default='none', max_length=40),
        ),
        migrations.AddField(
            model_name='patient',
            name='how_did_you_know_us',
            field=models.CharField(default='none', max_length=100),
        ),
    ]
