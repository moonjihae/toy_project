from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from employment.models import Employment
from payment.models import Payment
from payment.serializers import PaymentSerializer
from user.models import User
from lecture.models import Class
from django.urls import reverse
from django.http import Http404
import json


class PaymentListTest(TestCase):
    url = "/payment/"

    def setUp(self):
        self.client = APIClient()
        self.lecture = Class.objects.create(
            class_nm="test_class",
            academy="test_academy",
            start_dt="2021-03-10",
            end_dt="2021-05-10",
            isa_policy={
                "ctp": 2000000,
                "pay_per": 0.2,
                "deferm_cnt": 6,
                "limit_term": "2022-05-10",
                "min_income": 150000,
            },
        )
        self.user = User.objects.create(
            user_nm="testuser",
            phone="01000000",
            email="test@testuser.com",
            class_id=self.lecture,
        )
        self.emp = Employment.objects.create(
            company="test_company",
            salary=2000000,
            salary_ym="2020-09-08",
            emp_status=0,
            user_id=self.user,
        )
        self.payment_data = {
            "payment_ym": "2020-10-10",
            "monthly_pay": 400000,
            "payment_cnt": 6,
            "emp_id": self.emp.pk,
            "user_id": self.user.pk,
        }

        self.response = self.client.post(self.url, self.payment_data, format="json")

    # 납부 항목 생성
    def test_payment_registration(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_wrong_payment_registration(self):
        self.payment_data["emp_id"] = None
        self.response = self.client.post(self.url, self.payment_data, format="json")
        self.assertEqual(self.response.status_code, status.HTTP_400_BAD_REQUEST)

    # 납부 리스트 조회
    def test_get_payment_list(self):
        response = self.client.get(self.url, format="json")
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, serializer.data)


class PaymentDetailTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.lecture = Class.objects.create(
            class_nm="test_class",
            academy="test_academy",
            start_dt="2021-03-10",
            end_dt="2021-05-10",
            isa_policy={
                "ctp": 2000000,
                "pay_per": 0.2,
                "deferm_cnt": 6,
                "limit_term": "2022-05-10",
                "min_income": 150000,
            },
        )
        self.user = User.objects.create(
            user_nm="testuser",
            phone="01000000",
            email="test@testuser.com",
            class_id=self.lecture,
        )
        self.emp = Employment.objects.create(
            company="test_company",
            salary=2000000,
            salary_ym="2020-09-08",
            emp_status=0,
            user_id=self.user,
        )
        self.payment = Payment.objects.create(
            emp_id=self.emp,
            user_id=self.user,
            payment_ym=self.emp.salary_ym,
            monthly_pay=self.emp.salary * self.lecture.isa_policy["pay_per"],
            payment_cnt=self.lecture.isa_policy["deferm_cnt"],
        )
        self.url = reverse("payment_details", kwargs={"pk": self.payment.id})

    # 납부 개별 조회
    def test_PaymentDetail_can_get_a_payment(self):
        payment = Payment.objects.get()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, payment.id)

    def test_PaymentDetail_cannot_get_a_payment(self):
        response = self.client.get(reverse("payment_details", kwargs={"pk": 2}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 납부 수정
    def test_maximum_ctp_PaymentDetail_update(self):
        payment = Payment.objects.get()
        payment.payment_amt = self.lecture.isa_policy["ctp"] - payment.monthly_pay
        payment.save()
        response = self.client.patch(
            self.url,
            json.dumps(
                {
                    "payment_ym": self.payment.payment_ym,
                    "monthly_pay": self.payment.monthly_pay,
                    "payment_cnt": self.payment.payment_cnt,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "모든 납부가 종료되었습니다"})

    def test_finish_cnt_PaymentDetail_update(self):
        payment = Payment.objects.get()
        payment.payment_cnt = 1
        payment.save()
        response = self.client.patch(
            self.url,
            json.dumps(
                {
                    "payment_ym": self.payment.payment_ym,
                    "monthly_pay": self.payment.monthly_pay,
                    "payment_cnt": 0,
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "모든 납부가 종료되었습니다"})

    def test_wrong_PaymentDetail_update(self):
        response = self.client.patch(
            self.url,
            json.dumps({"payment_ym": "이천이십년 시월 십일"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_exist_PaymentDetail_update(self):
        response = self.client.patch("/payment/300")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 납부 삭제
    def test_PaymentDetail_delete(self):
        payment = Payment.objects.get()
        payment.payment_amt = 0
        payment.save()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_wrong_PaymentDetail_delete(self):
        payment = Payment.objects.get()
        payment.payment_amt = 1000
        payment.save()
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_exist_PaymentDetail_delete(self):
        response = self.client.delete("/payment/300")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)