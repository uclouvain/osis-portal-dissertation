# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-11 09:49
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dissertation', '0008_auto_20161010_0844'),
    ]

    operations = [
        migrations.CreateModel(
            name='PropositionOffer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offer_proposition', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dissertation.OfferProposition')),
                ('proposition_dissertation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dissertation.PropositionDissertation')),
            ],
        ),
    ]
