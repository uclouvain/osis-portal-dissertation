# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-09-19 11:51
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dissertation', '0026_auto_20190724_1034'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dissertation',
            name='education_group_year_start',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='dissertations', to='base.EducationGroupYear', verbose_name='Offers'),
        ),
    ]