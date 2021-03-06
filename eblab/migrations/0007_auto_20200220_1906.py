# Generated by Django 2.1.7 on 2020-02-21 00:06

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('eblab', '0006_auto_20190911_0203'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='usage_time',
            field=models.TimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='event',
            name='event',
            field=models.CharField(choices=[('LAS', 'Laser on'), ('LAE', 'Laser off'), ('LOI', 'Logged in'), ('LOO', 'Logged out'), ('NON', 'No action')], default='NON', max_length=3),
        ),
    ]
