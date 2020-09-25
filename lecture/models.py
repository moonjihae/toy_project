from django.db import models
from django.contrib.postgres.fields import JSONField


def default_isa_policy():
    return [
        {
            "ctp": 0,
            "min_income": 0,
            "limit_term": 0,
            "deferm_cnt": 0,
            "pay_per": 0,
        }
    ]


# Create your models here.
class Class(models.Model):

    class_nm = models.CharField(max_length=100, blank=False)
    academy = models.CharField(max_length=100, blank=False)
    start_dt = models.DateField(blank=False)
    end_dt = models.DateField(blank=False)
    isa_policy = JSONField(default=default_isa_policy)
