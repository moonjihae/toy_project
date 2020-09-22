# Generated by Django 3.1.1 on 2020-09-17 03:19

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('employment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='employment',
            name='emp_status',
            field=models.IntegerField(default=0, validators=[django.core.validators.MaxLengthValidator(2), django.core.validators.MinValueValidator(0)]),
        ),
    ]