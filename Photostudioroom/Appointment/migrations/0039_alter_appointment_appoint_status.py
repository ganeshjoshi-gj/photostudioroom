# Generated by Django 3.2.3 on 2021-06-01 00:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0038_alter_appointment_appoint_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='appoint_status',
            field=models.BooleanField(blank=True, default=True),
        ),
    ]
