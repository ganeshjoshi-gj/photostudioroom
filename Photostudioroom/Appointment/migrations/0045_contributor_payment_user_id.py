# Generated by Django 3.2.3 on 2021-06-05 00:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0044_alter_contributor_payment_total_amount'),
    ]

    operations = [
        migrations.AddField(
            model_name='contributor_payment',
            name='user_id',
            field=models.ForeignKey(db_column='user_id', default=None, on_delete=django.db.models.deletion.CASCADE, to='Appointment.user_details'),
            preserve_default=False,
        ),
    ]
