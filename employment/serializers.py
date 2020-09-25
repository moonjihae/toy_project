from rest_framework import serializers
from employment.models import Employment
from rest_framework.exceptions import ValidationError


class EmpCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employment
        fields = ["user_id", "company", "salary", "salary_ym", "emp_status"]


class EmpSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employment
        fields = "__all__"


class EmpUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employment
        fields = ["company", "salary"]
