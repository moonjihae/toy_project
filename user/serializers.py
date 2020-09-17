from rest_framework import serializers
from user.models import User
from rest_framework.exceptions import ValidationError

class UserCreateSerializer(serializers.ModelSerializer):
    user_nm=serializers.CharField(required=True,max_length=40)
    phone=serializers.CharField(required=True,max_length=25)
    email=serializers.CharField(required=True,max_length=60)
    
    class Meta:
        model=User
        fields=['user_nm','phone','email']
        
class UserSerializer(serializers.ModelSerializer):
     class Meta:
         model=User
         fields='__all__'

    

    

    
     