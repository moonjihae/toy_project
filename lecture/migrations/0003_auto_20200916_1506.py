# Generated by Django 3.1.1 on 2020-09-16 06:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lecture", "0002_auto_20200916_1441"),
    ]

    operations = [
        migrations.AlterField(
            model_name="class",
            name="end_dt",
            field=models.DateField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name="class",
            name="start_dt",
            field=models.DateField(auto_now=True),
        ),
    ]
