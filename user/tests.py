from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from user.models import User
from user.serializers import UserSerializer
from payment.models import Payment
from lecture.models import Class
from employment.models import Employment
from django.urls import reverse
from django.http import Http404
import json


class UserListTest(TestCase):
    url = "/user/"

    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "user_nm": "testuser",
            "email": "test@testuser.com",
            "phone": "01000000",
        }
        self.wrong_user_data = {
            "user_nm": "testuser",
            "email": "test@testuser.com",
            "phone": "",
        }

    # 회원 생성
    def test_user_registration(self):
        self.response = self.client.post(self.url, self.user_data, format="json")
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_wrong_user_registration(self):
        self.response = self.client.post(self.url, self.wrong_user_data, format="json")
        self.assertEqual(self.response.status_code, status.HTTP_400_BAD_REQUEST)

    # 회원 리스트 조회
    def test_get_user_list(self):
        response = self.client.get(self.url, format="json")
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, serializer.data)


class UserDetailTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_nm = "testuser"
        self.phone = "01000000"
        self.email = "test@testuser.com"

        self.user = User.objects.create(
            user_nm=self.user_nm, phone=self.phone, email=self.email
        )
        self.url = reverse("details", kwargs={"pk": self.user.id})
        self.lecture = Class.objects.create(
            class_nm="test_class",
            academy="test_academy",
            start_dt="2020-03-10",
            end_dt="2020-05-10",
            isa_policy={
                "ctp": 2000000,
                "pay_per": 0.2,
                "deferm_cnt": 6,
                "limit_term": "2022-05-10",
                "min_income": 150000,
            },
        )
        self.emp = Employment.objects.create(
            user_id=self.user,
            company="test_company",
            salary=2000000,
            salary_ym="2020-10-10",
            emp_status=0,
        )
        self.payment = Payment.objects.create(
            emp_id=self.emp,
            user_id=self.user,
            payment_ym="2020-10-10",
            monthly_pay=400000,
            payment_cnt=6,
        )

    # 회원 개별 조회
    def test_UserDetail_can_get_a_user(self):
        user = User.objects.get()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, user.id)

    def test_UserDetail_cannot_get_a_user(self):
        response = self.client.get(reverse("details", kwargs={"pk": 300}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 회원 수정
    def test_UserDetail_update(self):
        response = self.client.patch(self.url, {"class_id": self.lecture.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_UserDetail_update(self):
        response = self.client.patch(self.url, {"class_id": "test_class"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_exist_UserDetail_update(self):
        response = self.client.patch("/user/30")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 회원 삭제
    def test_UserDetail_delete(self):
        payment = Payment.objects.filter(user_id=self.user.id).last()
        payment.payment_amt = 0
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_wrongUserDetail_delete(self):
        wrong_payment = Payment.objects.create(
            emp_id=self.emp,
            user_id=self.user,
            payment_ym="2020-10-10",
            monthly_pay=400000,
            payment_cnt=6,
            payment_amt=1000,
        )
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_exist_UserDetail_delete(self):
        response = self.client.delete("/user/30")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
