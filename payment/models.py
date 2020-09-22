from django.db import models
from employment.models import Employment
from user.models import User

class Payment(models.Model):
    emp_id =models.ForeignKey(Employment,on_delete=models.CASCADE )
    user_id=models.ForeignKey(User,related_name="payments",on_delete=models.CASCADE)
    payment_ym=models.DateField(null=True)
    monthly_pay=models.IntegerField(default=0)
    payment_cnt=models.IntegerField()
    payment_amt=models.IntegerField(default=0)

