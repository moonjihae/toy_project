from rest_framework import serializers
from payment.models import Payment
from employment.models import Employment
from employment.serializers import EmpSerializer
from rest_framework.exceptions import ValidationError

class PaymentCreateSerailizer(serializers.ModelSerializer):

    class Meta:
        model=Payment
        fields=['emp_id',"user_id","payment_ym","monthly_pay","payment_cnt"]

class PaymentSerializer(serializers.ModelSerializer):
    # employment=serializers.SerializerMethodField()
    # def get_employment(self,instance):
    #     return empSerializer(instance.employment).data
    class Meta:
        model=Payment
        fields="__all__"


class PaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Payment
        fields=["payment_ym","monthly_pay","payment_cnt"]
    
    