# Generated by Django 2.1.7 on 2019-09-11 01:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eblab', '0004_auto_20190911_0018'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='rfid_tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='person', to='eblab.RFIDTag'),
        ),
    ]