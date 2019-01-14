# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-01-08 12:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dissertation', '0020_auto_20181217_1503'),
    ]

    operations = [
        migrations.AlterField(
            model_name='adviser',
            name='type',
            field=models.CharField(choices=[('PRF', 'Professor'), ('MGR', 'Course manager')], default='PRF', max_length=3),
        ),
        migrations.AlterField(
            model_name='dissertation',
            name='defend_periode',
            field=models.CharField(choices=[('UNDEFINED', 'undefined'), ('JANUARY', 'January'), ('JUNE', 'June'), ('SEPTEMBER', 'September')], default='UNDEFINED', max_length=12, null=True),
        ),
        migrations.AlterField(
            model_name='dissertation',
            name='status',
            field=models.CharField(choices=[('DRAFT', 'Draft'), ('DIR_SUBMIT', 'Submitted to promoter'), ('DIR_OK', 'Accepted by promoter'), ('DIR_KO', 'Refused by promoter'), ('COM_SUBMIT', 'Submitted to commission'), ('COM_OK', 'Accepted by commission'), ('COM_KO', 'Refused by commission'), ('EVA_SUBMIT', 'Submitted to first year evaluation'), ('EVA_OK', 'Accepted by first year evaluation'), ('EVA_KO', 'Refused by first year evaluation'), ('TO_RECEIVE', 'To be received'), ('TO_DEFEND', 'To be received defended'), ('DEFENDED', 'Defended'), ('ENDED', 'End'), ('ENDED_WIN', 'Win'), ('ENDED_LOS', 'Reported')], default='DRAFT', max_length=12),
        ),
        migrations.AlterField(
            model_name='dissertationupdate',
            name='status_from',
            field=models.CharField(choices=[('DRAFT', 'Draft'), ('DIR_SUBMIT', 'Submitted to promoter'), ('DIR_OK', 'Accepted by promoter'), ('DIR_KO', 'Refused by promoter'), ('COM_SUBMIT', 'Submitted to commission'), ('COM_OK', 'Accepted by commission'), ('COM_KO', 'Refused by commission'), ('EVA_SUBMIT', 'Submitted to first year evaluation'), ('EVA_OK', 'Accepted by first year evaluation'), ('EVA_KO', 'Refused by first year evaluation'), ('TO_RECEIVE', 'To be received'), ('TO_DEFEND', 'To be received defended'), ('DEFENDED', 'Defended'), ('ENDED', 'End'), ('ENDED_WIN', 'Win'), ('ENDED_LOS', 'Reported')], default='DRAFT', max_length=12),
        ),
        migrations.AlterField(
            model_name='dissertationupdate',
            name='status_to',
            field=models.CharField(choices=[('DRAFT', 'Draft'), ('DIR_SUBMIT', 'Submitted to promoter'), ('DIR_OK', 'Accepted by promoter'), ('DIR_KO', 'Refused by promoter'), ('COM_SUBMIT', 'Submitted to commission'), ('COM_OK', 'Accepted by commission'), ('COM_KO', 'Refused by commission'), ('EVA_SUBMIT', 'Submitted to first year evaluation'), ('EVA_OK', 'Accepted by first year evaluation'), ('EVA_KO', 'Refused by first year evaluation'), ('TO_RECEIVE', 'To be received'), ('TO_DEFEND', 'To be received defended'), ('DEFENDED', 'Defended'), ('ENDED', 'End'), ('ENDED_WIN', 'Win'), ('ENDED_LOS', 'Reported')], default='DRAFT', max_length=12),
        ),
        migrations.AlterField(
            model_name='propositiondissertation',
            name='type',
            field=models.CharField(choices=[('RDL', 'litterature_review'), ('EMP', 'empirical_research'), ('THE', 'theoretical_analysis'), ('PRO', 'project_dissertation'), ('DEV', 'My dissertations projects'), ('OTH', 'other')], default='RDL', max_length=12),
        ),
    ]