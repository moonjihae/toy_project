from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import UserCreateSerializer,UserSerializer
from .models import User
from payment.models import Payment



class UserList(APIView):
    #회원 정보 생성
    def post(self,request,format=None):
        serializer=UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True},status=status.HTTP_201_CREATED)
        else :
            return Response({"message ":'입력값이 유효하지 않습니다.'},status=status.HTTP_400_BAD_REQUEST)
    #회원 정보 리스트 조회
    def get(self,request,format=None):
        queryset=User.objects.all()
        serializer=UserSerializer(queryset,many=True)
        return Response(serializer.data)

class UserDatail(APIView):
    def get_object(self,pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"message":"Record not found"},status=status.HTTP_404_NOT_FOUND)
    #개별 회원 정보 조회
    def get (self,request,pk):
        user=self.get_object(pk)
        serializer=UserSerializer(user)
        return Response(serializer.data)

    #개별 회원 정보 수정
    def patch(self,request,pk,format=None):
        user=self.get_object(pk)
        serializer=UserSerializer(user,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True},status=status.HTTP_200_OK)
        return Response({"message":"입력값이 유효하지 않습니다."},status=status.HTTP_400_BAD_REQUEST)

    #개별 회원 정보 삭제
    def delete(self,request,pk,format=None):
        user=self.get_object(pk)
        payment=Payment.objects.filter(user_id=pk).latest()
        payment_amt=payment.payment_amt
        if(user.DoesNotExist):
            return Response({"message":"Record not found"},status=status.HTTP_404_NOT_FOUND)
        if (payment_amt==0):
            user.delete()
            return Response({'success': True},status=status.HTTP_204_NO_CONTENT)
        elif(payment_amt!=0):
            return Response({"message":"삭제 할 수 없습니다."},status=status.HTTP_400_BAD_REQUEST)
       