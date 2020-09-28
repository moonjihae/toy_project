from django.shortcuts import render
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import UserCreateSerializer, UserSerializer
from payment.serializers import PaymentSerializer
from .models import User
from payment.models import Payment


class UserList(APIView):
    # 회원 정보 생성
    def post(self, request, format=None):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True}, status=status.HTTP_201_CREATED)
        else:
            return Response(
                {"message ": "입력값이 유효하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST
            )

    # 회원 정보 리스트 조회
    def get(self, request, format=None):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)


class UserDetail(APIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404("Record not found")

    # 개별 회원 정보 조회
    def get(self, request, pk):
        user = self.get_object(pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    # 개별 회원 정보 수정
    def patch(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response(
            {"message": "입력값이 유효하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST
        )

    # 개별 회원 정보 삭제
    def delete(self, request, pk, format=None):
        try:
            user = self.get_object(pk)
        except (user.DoesNotExist):
            return Response(
                {"message": "Record not found"}, status=status.HTTP_404_NOT_FOUND
            )
        payment = Payment.objects.filter(user_id=pk).last()
        payment_amt = payment.payment_amt
        if payment is not None:
            if payment_amt is 0:
                user.delete()
                return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(
                    {"message": "이미 납부가 시작되어 삭제 할 수 없습니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        user.delete()
        return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)
