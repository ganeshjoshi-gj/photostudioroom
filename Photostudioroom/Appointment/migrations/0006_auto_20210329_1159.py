# Generated by Django 3.1.4 on 2021-03-29 06:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0005_auto_20210329_1157'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_details',
            name='userobj',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
