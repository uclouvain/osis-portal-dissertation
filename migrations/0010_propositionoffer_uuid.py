# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-11 11:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dissertation', '0009_propositionoffer'),
    ]

    operations = [
        migrations.AddField(
            model_name='propositionoffer',
            name='uuid',
            field=models.UUIDField(db_index=True, null=True),
        ),
    ]
