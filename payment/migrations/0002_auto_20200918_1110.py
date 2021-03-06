# Generated by Django 3.1.1 on 2020-09-18 02:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("employment", "0003_auto_20200918_1110"),
        ("user", "0001_initial"),
        ("payment", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="payment",
            name="emp_id",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.PROTECT, to="employment.employment"
            ),
        ),
        migrations.AlterField(
            model_name="payment",
            name="user_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="payments",
                to="user.user",
            ),
        ),
    ]
