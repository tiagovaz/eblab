# Generated by Django 2.1.7 on 2020-02-21 17:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eblab', '0012_auto_20200221_1219'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='log',
            name='laser_usage_time',
        ),
        migrations.RemoveField(
            model_name='log',
            name='logged_time',
        ),
    ]
