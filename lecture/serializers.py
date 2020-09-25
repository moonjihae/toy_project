from rest_framework import serializers
from lecture.models import Class
from rest_framework.exceptions import ValidationError
from .models import default_isa_policy


class ClassCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ["class_nm", "academy", "start_dt", "end_dt", "isa_policy"]

    def validate(self, data):
        if not data["start_dt"] < data["end_dt"]:
            msg = "입력값이 유효하지 않습니다!"
            raise serializers.ValidationError(msg)
        return data


class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = "__all__"
