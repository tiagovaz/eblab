# Generated by Django 2.1.7 on 2019-09-11 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eblab', '0005_auto_20190911_0117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='event',
            field=models.CharField(choices=[('LAS', 'Laser on'), ('LAE', 'Laser off'), ('LOI', 'Logged in'), ('LOO', 'Logged out'), ('NON', 'No action')], default='LOI', max_length=3),
        ),
    ]
