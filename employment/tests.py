from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from employment.models import Employment
from employment.serializers import EmpSerializer
from payment.models import Payment
from user.models import User
from lecture.models import Class
from django.urls import reverse
from django.http import Http404
import json


class EmpListTest(TestCase):
    url = "/employment/"

    def setUp(self):
        self.client = APIClient()
        self.emp_data = {
            "company": "test_company",
            "salary": 2000000,
            "salary_ym": "2020-09-08",
            "emp_status": 0,
        }

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
        user_id = self.user.id
        self.emp_data["user_id"] = user_id
        self.response = self.client.post(self.url, self.emp_data, format="json")

    def test_emp_registration(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_wrongUser_emp_registration(self):
        self.user.class_id = None
        self.response = self.client.post(self.url, self.emp_data, format="json")
        self.assertEqual(self.response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrongDate_emp_registration(self):
        self.lecture.isa_policy["lemit_term"] = "2019-10-10"
        self.response = self.client.post(self.url, self.emp_data, format="json")
        self.assertEqual(self.response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_emp_list(self):
        response = self.client.get(self.url, format="json")
        emps = Employment.objects.all()
        serializer = EmpSerializer(emps, many=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, serializer.data)


class EmpDetailTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.emp_data = {
            "company": "test_company",
            "salary": 2000000,
            "salary_ym": "2020-09-08",
            "emp_status": 0,
        }
        self.valid_emp_data = {
            "company": "test2_company",
            "salary": 10000000,
            "salary_ym": "2020-09-08",
            "emp_status": 0,
        }
        self.invalid_emp_data = {
            "company": "",
            "salary": 2000000,
            "salary_ym": "2020-09-08",
            "emp_status": 0,
        }
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
            monthly_pay=40000000,
            payment_cnt=6,
        )
        self.url = reverse("emp_details", kwargs={"pk": self.emp.id})

    def test_EmpDetail_can_get_a_employment(self):
        emp = Employment.objects.get()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, emp.id)

    def test_EmpDetail_cannot_get_a_employment(self):
        response = self.client.get(reverse("emp_details", kwargs={"pk": 30}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_EmpDetail_update(self):
        response = self.client.patch(
            self.url,
            json.dumps({"company": "test2_company", "salary": 10000000}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_status_EmpDetail_update(self):
        emp = Employment.objects.get()
        emp.emp_status = 0
        response = self.client.patch(
            self.url,
            json.dumps({"company": "test2_company", "salary": 10000000}),
            content_type="application/json",
        )

    def test_mininum_salary_EmpDetail_update(self):
        response = self.client.patch(
            self.url,
            json.dumps({"company": "test2_company", "salary": 100}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_EmpDetail_update(self):
        response = self.client.patch(
            self.url,
            json.dumps({"company": "test2_company", "salary": "백만원"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_EmpDetail_delete(self):
        payment = Payment.objects.get(emp_id=self.emp.id)
        payment.payment_amt = 0
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class EmpStatusTest(TestCase):
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
            monthly_pay=40000000,
            payment_cnt=6,
        )
        self.url = reverse("emp_status", kwargs={"pk": self.emp.id})

    def test_0_empStatus_update(self):
        response = self.client.patch(
            self.url,
            json.dumps({"emp_status": 0}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_1_empStatus_update(self):
        response = self.client.patch(
            self.url,
            json.dumps({"emp_status": 1}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_2_empStatus_update(self):
        response = self.client.patch(
            self.url,
            json.dumps({"emp_status": 2}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_empStatus_update(self):
        response = self.client.patch(
            self.url,
            json.dumps({"emp_status": 4}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
