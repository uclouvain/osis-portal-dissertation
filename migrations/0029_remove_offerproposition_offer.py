# Generated by Django 2.2.10 on 2020-12-10 14:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dissertation', '0028_auto_20191209_1358'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offerproposition',
            name='offer',
        ),
    ]