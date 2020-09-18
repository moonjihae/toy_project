from rest_framework import serializers
from lecture.models import Class
from rest_framework.exceptions import ValidationError
from .models import default_isa_policy


class ClassCreateSerializer(serializers.ModelSerializer):
    class_nm=serializers.CharField(required=True,max_length=100)
    academy=serializers.CharField(required=True,max_length=100)
    start_dt=serializers.DateField(required=True)
    end_dt=serializers.DateField(required=True)
    # isa_policy=serializers.JSONField(required=True)

    class Meta:
        model=Class
        fields=['class_nm','academy','start_dt','end_dt']
        extra_kwargs = {'class_nm': {'required': True},'academy': {'required':True},
                        'start_dt': {'required': True},'end_dt': {'required': True}}

    def validate(self,data):
            if not data['start_dt']<data['end_dt']:
                msg="입력값이 유효하지 않습니다!"
                raise serializers.ValidationError(msg)  
            return data
        
  
            

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model=Class
        fields='__all__'