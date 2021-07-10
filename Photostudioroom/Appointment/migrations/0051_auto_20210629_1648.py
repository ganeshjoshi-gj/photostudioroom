# Generated by Django 3.2.3 on 2021-06-29 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0050_alter_images_total_earnings'),
    ]

    operations = [
        migrations.AddField(
            model_name='remaining_contributor_payment_details',
            name='amount',
            field=models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=8, null=True),
        ),
        migrations.AlterField(
            model_name='remaining_contributor_payment',
            name='total_amount',
            field=models.DecimalField(blank=True, decimal_places=0, default=0, max_digits=8, null=True),
        ),
    ]
