from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import PaymentCreateSerailizer,PaymentSerializer,PaymentUpdateSerializer
from .models import Payment
from employment.models import Employment
from user.models import User
from lecture.models import Class
import datetime
from django.utils.dateformat import DateFormat

class PaymentList(APIView):
    #납부 정보 생성
    def post(self,request,format=None):
        serializer=PaymentCreateSerailizer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success":True},status=status.HTTP_201_CREATED)

        else:
            return Response({"입력값이 유효하지 않습니다."},status=status.HTTP_400_BAD_REQUEST)

    def get(self,request,format=None):
        queryset=Payment.objects.all()
        serializer=PaymentSerializer(queryset,many=True)
        return Response(serializer.data)


class PaymentDetail(APIView):
    def get_object(self,pk):
        try:
            return Payment.objects.get(pk=pk)
        except Payment.DoesNotExist:
            return Response({"message":"Record not found"},status=status.HTTP_404_NOT_FOUND)

    #개별 납부 조회
    def get(self,request,pk,format=None):
        payment=self.get_object(pk)
        serializer=PaymentSerializer(payment)
        return Response(serializer.data)
        
    #개별 납부 수정
    def patch(self,request,pk,format=None):
        payment=self.get_object(pk)
        payment.payment_cnt-=1
        serializer=PaymentUpdateSerializer(payment,data=request.data)
        class_id=User.objects.get(pk=payment.user_id.pk).class_id.pk
        lecture=Class.objects.get(pk=class_id)
        ctp=lecture.isa_policy[0]['ctp']
        if( payment.payment_cnt>=1):
            payment.payment_ym=payment.payment_ym+datetime.timedelta(days=30)
            payment.payment_ym=payment.payment_ym.strftime("%Y-%m-%d")
            emp=Employment.objects.get(pk=payment.emp_id.pk)
            emp.salary_ym=payment.payment_ym
            emp.save()
            payment.payment_amt+=payment.monthly_pay
            if ctp-payment.payment_amt<payment.monthly_pay:
                payment.monthly_pay=ctp-payment.payment_amt
            if payment.payment_amt==ctp:
                payment.payment_amt=ctp
                payment.payment_ym=None
                payment.payment_cnt=0
                payment.monthly_pay=0
                payment.save()
                return Response({"message":"모든 납부가 종료되었습니다"})
            payment.save()
            return Response({"success":True},status=status.HTTP_200_OK)
        elif (payment.payment_cnt==0):
            payment.payment_ym=None
            payment.save()
            return Response({"message":"모든 납부가 종료되었습니다"})
       
       
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"모든 납부가 종료되었습니다"})
        return Response({"message":"입력값이 유효하지 않습니다."},status=status.HTTP_400_BAD_REQUEST)
    #개별 납부 삭제
    def delete(self,request,pk,format=None):
        payment=self.get_object(pk)
        if payment.payment_amt is 0:
            emp=Employment.objects.get(pk=payment.emp_id.pk)
            payment.delete()
            emp.delete()
            return Response({"success":True})
        return Response({"message":"이미 납부가 시작되어 삭제 할 수 없습니다."},status=status.HTTP_400_BAD_REQUEST)
