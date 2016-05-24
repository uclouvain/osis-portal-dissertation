# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-23 09:40
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BasePerson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('changed', models.DateTimeField(null=True)),
                ('global_id', models.CharField(blank=True, max_length=10, null=True)),
                ('gender', models.CharField(blank=True, choices=[('F', 'female'), ('M', 'male'), ('U', 'unknown')], default='U', max_length=1, null=True)),
                ('national_id', models.CharField(blank=True, max_length=25, null=True)),
                ('first_name', models.CharField(blank=True, db_index=True, max_length=50, null=True)),
                ('middle_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, db_index=True, max_length=50, null=True)),
                ('email', models.EmailField(blank=True, max_length=255, null=True)),
                ('phone', models.CharField(blank=True, max_length=30, null=True)),
                ('phone_mobile', models.CharField(blank=True, max_length=30, null=True)),
                ('language', models.CharField(choices=[('fr-be', 'French'), ('en', 'English')], default='fr-be', max_length=30, null=True)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]