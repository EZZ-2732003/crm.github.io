# Generated by Django 5.1 on 2024-12-04 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0045_remove_reserve_name_reserve_patient_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reserve',
            name='service_details',
        ),
        migrations.RemoveField(
            model_name='reserve',
            name='service',
        ),
        migrations.AddField(
            model_name='reserve',
            name='service',
            field=models.CharField(choices=[('Consultation', 'Consultation'), ('Retouch', 'Retouch'), ('Retouch: filler_nose', 'Retouch: Filler Nose'), ('Retouch: filler_lip', 'Retouch: Filler Lip'), ('Retouch: botox', 'Retouch: Botox'), ('botox', 'Botox'), ('filler_face', 'Filler Face'), ('filler_nose', 'Filler Nose'), ('filler_lip', 'Filler Lip'), ('skin_booster_syringe', 'Skin Booster Syringe'), ('skin_booster_injection', 'Skin Booster Injection'), ('dissolving_filler', 'Dissolving Filler'), ('dermapen', 'Dermapen'), ('plasmage', 'Plasmage')], default='service', max_length=100),
        ),
    ]