from rest_framework import serializers
from user.models import User
from rest_framework.exceptions import ValidationError
from employment.models import Employment
from employment.serializers import EmpSerializer
from payment.serializers import PaymentSerializer
from lecture.serializers import ClassSerializer


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["user_nm", "phone", "email"]


class UserSerializer(serializers.ModelSerializer):

    employments = serializers.SerializerMethodField()
    payments = serializers.SerializerMethodField()

    def get_employments(self, instance):
        return EmpSerializer(instance.employments, many=True).data

    def get_payments(self, instance):
        return PaymentSerializer(instance.payments, many=True).data

    class Meta:
        model = User
        fields = [
            "id",
            "class_id",
            "user_nm",
            "phone",
            "email",
            "employments",
            "payments",
        ]
