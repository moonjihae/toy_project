from django.db import models
from lecture.models import Class

# Create your models here.
class User(models.Model):
    class_id = models.ForeignKey(Class, null=True, on_delete=models.SET_NULL)
    user_nm = models.CharField(max_length=40)
    phone = models.CharField(max_length=25)
    email = models.EmailField(max_length=60)
