# Generated by Django 2.1.7 on 2020-02-21 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eblab', '0007_auto_20200220_1906'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='usage_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
