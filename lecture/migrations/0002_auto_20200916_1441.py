# Generated by Django 3.1.1 on 2020-09-16 05:41

import django.contrib.postgres.fields.jsonb
from django.db import migrations
import lecture.models


class Migration(migrations.Migration):

    dependencies = [
        ('lecture', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='isa_policy',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=lecture.models.default_isa_policy),
        ),
    ]