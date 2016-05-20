# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-20 08:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reference', '0003_educationinstitution_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationinstitution',
            name='institution_type',
            field=models.CharField(choices=[('SECONDARY', 'Secondaire'), ('UNIVERSITY', 'University'), ('HIGHER_NON_UNIVERSITY', 'Higher non-university')], max_length=25),
        ),
    ]
