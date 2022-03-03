# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-10-11 10:25
from __future__ import unicode_literals

from django.db import connection
from django.db import migrations

from dissertation.models.proposition_offer import PropositionOffer


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
        ]


def move_data_from_offer_proposition_to_proposition_offer(apps, schema_editor):
    cursor = connection.cursor()
    cursor.execute("select * from dissertation_propositiondissertation_offer_proposition")
    for record in dictfetchall(cursor):
        proposition_dissertation_id = record['propositiondissertation_id']
        offer_proposition_id = record['offerproposition_id']
        offer = PropositionOffer()
        offer.proposition_dissertation_id = proposition_dissertation_id
        offer.offer_proposition_id = offer_proposition_id
        offer.save()


class Migration(migrations.Migration):

    dependencies = [
        ('dissertation', '0012_remove_null'),
    ]

    operations = [
        migrations.RunPython(move_data_from_offer_proposition_to_proposition_offer, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='propositiondissertation',
            name='offer_proposition',
        ),
    ]
