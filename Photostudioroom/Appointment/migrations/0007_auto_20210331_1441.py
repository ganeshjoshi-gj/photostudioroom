# Generated by Django 3.1.4 on 2021-03-31 09:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0006_auto_20210329_1159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateField(blank=True, default=None, null=True),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_time',
            field=models.TimeField(blank=True, default=None, null=True),
        ),
    ]
