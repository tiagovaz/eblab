# Generated by Django 2.1.7 on 2020-02-21 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eblab', '0011_eventdaily_logdaily'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='laser_usage_time',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='log',
            name='logged_time',
            field=models.DurationField(blank=True, null=True),
        ),
    ]