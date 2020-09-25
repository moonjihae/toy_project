from django.db import models
from user.models import User
from django.core.validators import MaxLengthValidator, MinValueValidator


class Employment(models.Model):
    user_id = models.ForeignKey(
        User, related_name="employments", null=False, on_delete=models.CASCADE
    )
    company = models.CharField(max_length=100)
    salary = models.IntegerField()
    salary_ym = models.DateField()
    emp_status = models.IntegerField()
