# Generated by Django 5.2.4 on 2025-07-25 07:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_booking_class_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='train',
            options={'ordering': ['name'], 'verbose_name': 'Train', 'verbose_name_plural': 'Trains'},
        ),
        migrations.AlterField(
            model_name='train',
            name='arrival_time',
            field=models.TimeField(blank=True, null=True, verbose_name='Arrival Time'),
        ),
        migrations.AlterField(
            model_name='train',
            name='class_type',
            field=models.ManyToManyField(blank=True, help_text='Select all available classes for this train', to='app.classtype', verbose_name='Class Types'),
        ),
        migrations.AlterField(
            model_name='train',
            name='departure_time',
            field=models.TimeField(blank=True, null=True, verbose_name='Departure Time'),
        ),
        migrations.AlterField(
            model_name='train',
            name='destination',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='arriving_trains', to='app.station', verbose_name='Destination Station'),
        ),
        migrations.AlterField(
            model_name='train',
            name='nos',
            field=models.PositiveIntegerField(blank=True, help_text='Total number of available seats on the train', null=True, verbose_name='Number of Seats'),
        ),
        migrations.AlterField(
            model_name='train',
            name='source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='departing_trains', to='app.station', verbose_name='Source Station'),
        ),
    ]
