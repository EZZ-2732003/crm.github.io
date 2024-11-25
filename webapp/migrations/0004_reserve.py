# Generated by Django 5.1 on 2024-09-10 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0003_delete_reserve'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reserve',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('birth', models.DateField()),
                ('phone', models.IntegerField()),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('create_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]