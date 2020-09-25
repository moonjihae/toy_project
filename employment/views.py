from django.shortcuts import render
from django.http import Http404

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from .serializers import EmpCreateSerializer, EmpSerializer, EmpUpdateSerializer
from user.serializers import UserSerializer
from lecture.serializers import ClassSerializer
from .models import Employment
from user.models import User
from lecture.models import Class
from payment.models import Payment
from payment.views import PaymentDetail
from payment.serializers import PaymentCreateSerailizer, PaymentSerializer
import datetime
import json
from dateutil import relativedelta
from collections import OrderedDict


class EmpList(APIView):
    # 취업 정보 생성
    def post(self, request, format=None):
        user = User.objects.get(pk=request.data["user_id"])
        if user is None:
            return Response(
                {"message": "해당 회원이 존재하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        emps = Employment.objects.filter(user_id=user.id, emp_status=0)
        if emps.count() != 0:
            return Response(
                {"message": "이미 재직 중인 취업처가 존재합니다"}, status=status.HTTP_400_BAD_REQUEST
            )
        class_id = user.class_id.pk

        if class_id is not None:
            lecture = Class.objects.get(pk=class_id)
            limit_term = lecture.isa_policy["limit_term"]
            limit_term = datetime.datetime.strptime(limit_term, "%Y-%m-%d")
            if (limit_term - datetime.datetime.now()).days > 0:
                min_income = lecture.isa_policy["min_income"]
                if int(request.data["salary"]) < min_income:
                    return Response(
                        {"message": "급여가 최소 급여 조건보다 적습니다."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                serializer = EmpCreateSerializer(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    emp_id = Employment.objects.latest("id")
                    user_id = User.objects.get(pk=request.data["user_id"])
                    payment_ym = request.data["salary_ym"]
                    monthly_pay = (int(request.data["salary"])) * (
                        lecture.isa_policy["pay_per"]
                    )
                    # 1원 반올림해주기
                    monthly_pay = (monthly_pay + 5) // 10 * 10
                    ctp = lecture.isa_policy["ctp"]
                    if monthly_pay > ctp:
                        monthly_pay = ctp
                        monthly_pay = (monthly_pay + 5) / 10 * 10
                    payment_cnt = lecture.isa_policy["deferm_cnt"]
                    payment_ym = datetime.datetime.strptime(payment_ym, "%Y-%m-%d")
                    diff_months = relativedelta.relativedelta(
                        limit_term, payment_ym
                    ).months

                    if diff_months < payment_cnt:
                        payment_cnt = diff_months
                    payment_instance = Payment(
                        emp_id=emp_id,
                        user_id=user_id,
                        payment_ym=payment_ym,
                        monthly_pay=monthly_pay,
                        payment_cnt=payment_cnt,
                    )
                    payment_instance.save()
                    return Response({"success": True}, status=status.HTTP_201_CREATED)
        return Response(
            {"message": "입력값이 유효하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST
        )

    # 취업 정보 리스트 조회
    def get(self, request, format=None):
        queryset = Employment.objects.all()
        serializer = EmpSerializer(queryset, many=True)
        return Response(serializer.data)


class EmpDetail(APIView):
    def get_object(self, pk):
        try:
            return Employment.objects.get(pk=pk)
        except Employment.DoesNotExist:
            raise Http404

    # 취업 정보 개별 조회
    def get(self, request, pk):
        emp = self.get_object(pk)
        serializer = EmpSerializer(emp)
        return Response(serializer.data)

    # 취업 정보 개별 수정
    def patch(self, request, pk, format=None):
        emp = self.get_object(pk)
        serializer = EmpUpdateSerializer(emp, data=request.data, partial=True)
        if emp.emp_status != 0:
            return Response(
                {"message": "취업 정보 변경을 할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST
            )
        if serializer.is_valid():
            serializer.save()
            payment = Payment.objects.get(emp_id=pk)
            user_id = EmpSerializer(emp).data["user_id"]
            user = User.objects.get(pk=user_id)
            class_id = UserSerializer(user).data["class_id"]
            lecture = Class.objects.get(pk=class_id)
            ctp = lecture.isa_policy[0]["ctp"]
            pay_per = lecture.isa_policy[0]["pay_per"]
            if request.data["salary"] < lecture.isa_policy[0]["min_income"]:
                return Response(
                    {"message": "급여가 최소 급여 조건보다 적습니다"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if payment.payment_amt + (request.data["salary"] * pay_per) > ctp:
                payment.monthly_pay = ctp - payment.payment_amt
            else:
                payment.monthly_pay = (emp.salary) * pay_per

            payment.monthly_pay = (payment.monthly_pay + 5) // 10 * 10
            payment.save()
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response(
            {"message": "입력값이 유효하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST
        )

    # 취업 정보 개별 삭제
    def delete(self, request, pk, format=None):
        employment = self.get_object(pk)
        payment = Payment.objects.get(emp_id=pk)
        if payment.payment_amt is 0:
            employment.delete()
            return Response({"success": True}, status=status.HTTP_200_OK)
        return Response(
            {"message": "이미 납부가 시작되어 삭제 할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST
        )


class EmpStatus(APIView):
    # 취업 상태 개별 수정
    def get_object(self, pk):
        try:
            return Employment.objects.get(pk=pk)
        except Employment.DoesNotExist:
            raise Http404

    def patch(self, request, pk, format=None):
        employment = self.get_object(pk)
        serializer = EmpSerializer(employment)
        user_id = serializer.data["user_id"]
        status = request.data["emp_status"]
        if status == 0:
            payments = Payment.objects.filter(user_id=user_id).exclude(emp_id=pk)
            payment = Payment.objects.get(emp_id=pk)
            if payment is not None:
                user = User.objects.get(pk=serializer.data["user_id"])
                class_id = user.class_id.pk
                lecture = Class.objects.get(pk=class_id)
                ctp = lecture.isa_policy[0]["ctp"]
                payment.monthly_pay = (employment.salary) * lecture.isa_policy[0][
                    "pay_per"
                ]
                if payment.payment_amt + payment.monthly_pay > ctp:
                    payment.monthly_pay = ctp - payment.payment_amt
                payment.monthly_pay = (payment.monthly_pay + 5) // 10 * 10
                payment.payment_ym = employment.salary_ym
                payment.save()
            # 나머지 납부 항목들 초기화
            if payments is not None:
                payments.update(payment_ym=None)
                payments.update(monthly_pay=0)
                serializer = EmpSerializer(employment, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"success": True})
                return Response(
                    {"message": "입력값이 유효하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST
                )
        if status == 1:
            payment = Payment.objects.get(emp_id=pk)
            if payment is not None:
                payment.payment_ym = None
                payment.monthly_pay = "0"
                payment.save()
                serializer = EmpSerializer(employment, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"success": True})
                return Response(
                    {"message": "입력값이 유효하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST
                )
        if status == 2:
            payment = Payment.objects.get(emp_id=pk)
            emp = Employment.objects.get(user_id=user_id, emp_status=0)
            new_payment = Payment.objects.get(emp_id=emp)
            if payment is not None:
                new_payment.payment_amt = payment.payment_amt
                new_payment.payment_cnt = payment.payment_cnt
                user = User.objects.get(pk=serializer.data["user_id"])
                class_id = user.class_id.pk
                lecture = Class.objects.get(pk=class_id)
                ctp = lecture.isa_policy[0]["ctp"]
                new_payment.monthly_pay = (employment.salary) * lecture.isa_policy[0][
                    "pay_per"
                ]

                if new_payment.payment_amt + new_payment.monthly_pay > ctp:
                    new_payment.monthly_pay = ctp - new_payment.payment_amt
                new_payment.monthly_pay = (new_payment.monthly_pay + 5) // 10 * 10
                new_payment.save()
                serializer = EmpSerializer(employment, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({"success": True})

        elif status != 0 or status != 1 or status != 2:
            return Response({"message": "상태 정보는 0(재직), 1(퇴사), 2(이직) 중에서만 선택가능합니다."})
