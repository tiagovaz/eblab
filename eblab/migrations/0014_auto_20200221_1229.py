# Generated by Django 2.1.7 on 2020-02-21 17:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eblab', '0013_auto_20200221_1228'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='laser_usage_time',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='log',
            name='logged_time',
            field=models.DurationField(blank=True, null=True),
        ),
    ]
