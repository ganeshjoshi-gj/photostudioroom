# Generated by Django 3.1.4 on 2021-03-29 05:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0003_auto_20210329_1116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_details',
            name='address_id',
            field=models.ForeignKey(blank=True, db_column='address_id', default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='Appointment.address'),
        ),
    ]
