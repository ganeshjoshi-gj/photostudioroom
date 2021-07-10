# Generated by Django 3.1.4 on 2021-04-08 00:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Appointment', '0013_auto_20210407_0934'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like_Details',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_id', models.ForeignKey(db_column='image_id', on_delete=django.db.models.deletion.CASCADE, to='Appointment.image')),
                ('user_id', models.ForeignKey(db_column='user_id', on_delete=django.db.models.deletion.CASCADE, to='Appointment.user_details')),
            ],
            options={
                'verbose_name_plural': 'Like Details',
                'db_table': 'Like_Details',
            },
        ),
    ]
