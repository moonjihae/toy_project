from django.shortcuts import render
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import ClassCreateSerializer, ClassSerializer
from .models import Class
from payment.models import Payment
from payment.serializers import PaymentSerializer
from user.models import User
from user.serializers import UserSerializer
import datetime


class ClassList(APIView):
    # 강의 생성
    def post(self, request, format=None):
        request.data["isa_policy"]["ctp"] = (
            (request.data["isa_policy"]["ctp"] + 5) // 10 * 10
        )
        serializer = ClassCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"message": "입력값이 유효하지 않습니다?"}, status=status.HTTP_400_BAD_REQUEST
            )

    # 강의 정보 리스트 조회
    def get(self, request, format=None):
        queryset = Class.objects.all()
        serializer = ClassSerializer(queryset, many=True)
        return Response(serializer.data)


class ClassDetail(APIView):
    def get_object(self, pk):
        try:
            return Class.objects.get(pk=pk)
        except Class.DoesNotExist:
            raise Http404("Record not found")

    # 개별 강의 조회
    def get(self, request, pk):
        lecture = self.get_object(pk)
        serializer = ClassSerializer(lecture)
        return Response(serializer.data)

    # 개별 강의 수정
    def patch(self, request, pk, format=None):

        lecture = self.get_object(pk)

        serializer = ClassSerializer(lecture, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            lecture.isa_policy["ctp"] = (lecture.isa_policy["ctp"] + 5) // 10 * 10
            lecture.save()

            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response(
            {"message": "입력값이 유효하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST
        )

    # 개별 강의 삭제
    def delete(self, request, pk, format=None):
        lecture = self.get_object(pk)
        start_dt = lecture.start_dt

        if (start_dt - datetime.date.today()).days < 0:
            return Response(
                {"message": "강의가 이미 시작되었습니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(class_id=pk)
        user = UserSerializer(user, many=True).data
        if user is not None:
            for i in range(len(user)):
                user_id = user[i]["id"]
                if Payment.objects.filter(user_id=user_id).exists():
                    payment = Payment.objects.get(user_id=user_id)
                    payment_amt = PaymentSerializer(payment).data["payment_amt"]
                    if payment_amt > 0:
                        return Response(
                            {"message": "삭제 할 수 없습니다."},
                            status=status.HTTP_400_BAD_REQUEST,
                        )
            lecture.delete()
            return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)
        else:
            lecture.delete()
            return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)
