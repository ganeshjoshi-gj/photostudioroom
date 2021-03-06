# Generated by Django 3.2.3 on 2021-05-28 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0032_auto_20210528_1941'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='event_duration',
        ),
        migrations.AddField(
            model_name='address',
            name='saved_address_name',
            field=models.CharField(blank=True, default=None, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='eventdays',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='gears',
            field=models.CharField(blank=True, choices=[('Cameras', 'Cameras'), ('C+D', 'Cameras + Drone')], default=None, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='photo_quantity',
            field=models.IntegerField(blank=True, default=None, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='service',
            field=models.CharField(blank=True, choices=[('Photo', 'Photography'), ('Video', 'Videography'), ('Both', 'Videography + Photography')], default=None, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='video_duration',
            field=models.CharField(blank=True, choices=[('1-2', '1-2 Minutes'), ('2-3', '2-3 Minutes'), ('3-4', '3-4 Minutes'), ('4-5', '4-5 Minutes'), ('5-6', '5-6 Minutes'), ('6-7', '6-7 Minutes'), ('7-8', '7-8 Minutes')], default=None, max_length=15, null=True),
        ),
    ]
