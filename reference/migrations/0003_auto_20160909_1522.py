# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-09 15:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0011_auto_20160909_1522'),
        ('reference', '0002_domain'),
    ]

    operations = [
        migrations.CreateModel(
            name='Decree',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(max_length=80, unique=True)),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ExternalOffer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(null=True)),
                ('name', models.CharField(max_length=150, unique=True)),
                ('adhoc', models.BooleanField(default=True)),
                ('national', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='InstitutionalGradeType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.RemoveField(
            model_name='gradetype',
            name='grade',
        ),
        migrations.AddField(
            model_name='assimilationcriteria',
            name='external_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='assimilationcriteria',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name='country',
            name='external_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='country',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name='domain',
            name='national',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='domain',
            name='reference',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='domain',
            name='type',
            field=models.CharField(choices=[('HIGH_EDUC_NOT_UNIVERSITY', 'HIGH_EDUC_NOT_UNIVERSITY'), ('UNIVERSITY', 'UNIVERSITY'), ('UNKNOWN', 'UNKNOWN')], default='UNKNOWN', max_length=50),
        ),
        migrations.AddField(
            model_name='domain',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name='educationinstitution',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name='educationtype',
            name='external_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='educationtype',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name='gradetype',
            name='adhoc',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='gradetype',
            name='coverage',
            field=models.CharField(choices=[('HIGH_EDUC_NOT_UNIVERSITY', 'HIGH_EDUC_NOT_UNIVERSITY'), ('UNIVERSITY', 'UNIVERSITY'), ('UNKNOWN', 'UNKNOWN')], default='UNKNOWN', max_length=30),
        ),
        migrations.AddField(
            model_name='gradetype',
            name='institutional',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='gradetype',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name='language',
            name='external_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='language',
            name='uuid',
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='educationinstitution',
            name='institution_type',
            field=models.CharField(choices=[('SECONDARY', 'SECONDARY'), ('UNIVERSITY', 'UNIVERSITY'), ('HIGHER_NON_UNIVERSITY', 'HIGHER_NON_UNIVERSITY')], max_length=25),
        ),
        migrations.AlterField(
            model_name='educationinstitution',
            name='national_community',
            field=models.CharField(blank=True, choices=[('FRENCH', 'FRENCH'), ('GERMAN', 'GERMAN'), ('DUTCH', 'DUTCH')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='externaloffer',
            name='domain',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference.Domain'),
        ),
        migrations.AddField(
            model_name='externaloffer',
            name='grade_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='reference.GradeType'),
        ),
        migrations.AddField(
            model_name='externaloffer',
            name='offer_year',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.OfferYear'),
        ),
        migrations.AddField(
            model_name='domain',
            name='decree',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reference.Decree'),
        ),
        migrations.AddField(
            model_name='gradetype',
            name='institutional_grade_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='reference.InstitutionalGradeType'),
        ),
    ]
