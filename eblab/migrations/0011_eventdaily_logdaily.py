# Generated by Django 2.1.7 on 2020-02-21 16:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eblab', '0010_auto_20200221_1053'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventDaily',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event', models.CharField(choices=[('LASER', 'Laser'), ('LOGIN', 'Login')], max_length=5)),
            ],
        ),
        migrations.CreateModel(
            name='LogDaily',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('usage_time', models.DurationField()),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eblab.EventDaily')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eblab.Person')),
                ('rfid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eblab.RFIDTag')),
            ],
        ),
    ]
