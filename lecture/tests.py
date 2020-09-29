from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from lecture.models import Class
from lecture.serializers import ClassSerializer
from user.models import User
from employment.models import Employment
from payment.models import Payment
from django.urls import reverse
from django.http import Http404
import json


class LectureListTest(TestCase):
    url = "/lecture/"

    def setUp(self):
        self.client = APIClient()
        self.lecture_data = {
            "class_nm": "test_class",
            "academy": "test_academy",
            "start_dt": "2020-03-10",
            "end_dt": "2020-05-10",
            "isa_policy": {
                "ctp": 2000000,
                "pay_per": 0.2,
                "deferm_cnt": 6,
                "limit_term": "2021-05-10",
                "min_income": 150000,
            },
        }
        self.wrong_lecture_data = {
            "class_nm": "test_class",
            "academy": "test_academy",
            "start_dt": "이천이십년 삼월 십일",
            "end_dt": "2020-05-10",
            "isa_policy": {
                "ctp": 2000000,
                "pay_per": 0.2,
                "deferm_cnt": 6,
                "limit_term": "2021-05-10",
                "min_income": 150000,
            },
        }

    # 강의 생성
    def test_lecture_registration(self):
        self.response = self.client.post(self.url, self.lecture_data, format="json")
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_wrong_lecture_registration(self):
        self.response = self.client.post(
            self.url, self.wrong_lecture_data, format="json"
        )
        self.assertEqual(self.response.status_code, status.HTTP_400_BAD_REQUEST)

    # 강의 리스트 조회
    def test_get_lecture_list(self):
        response = self.client.get(self.url, format="json")
        lectures = Class.objects.all()
        serializer = ClassSerializer(lectures, many=True)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, serializer.data)


class LectureDetailTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.class_nm = "test_class"
        self.academy = "test_academy"
        self.start_dt = "2020-10-10"
        self.end_dt = "2020-12-10"
        self.isa_policy = {
            "ctp": 100031,
            "pay_per": 0.35,
            "deferm_cnt": 5,
            "limit_term": "2022-01-01",
            "min_income": 20000,
        }
        self.lecture = Class.objects.create(
            class_nm=self.class_nm,
            academy=self.academy,
            start_dt=self.start_dt,
            end_dt=self.end_dt,
            isa_policy=self.isa_policy,
        )
        self.url = reverse("lecture_details", kwargs={"pk": self.lecture.id})

        self.user = User.objects.create(
            user_nm="test_user",
            class_id=self.lecture,
            phone="01000000000",
            email="test@testuser.com",
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

    # 강의 개별조회
    def test_LectureDetail_can_get_a_lecture(self):
        lecture = Class.objects.get()
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, lecture.id)

    def test_LectureDetail_cannot_get_a_lecture(self):
        response = self.client.get(reverse("lecture_details", kwargs={"pk": 30}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 강의 수정
    def test_LectureDetail_update(self):
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_wrong_LectureDetail_update(self):
        response = self.client.patch(self.url, {"start_dt": "이천이십년 삼월 십일"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_not_exist_LectureDetail_update(self):
        response = self.client.patch("/lecture/300")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # 강의 삭제
    def test_LectureDetail_delete(self):

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_wrongDate_lectureDetail_delete(self):
        wrong_lecture = Class.objects.create(
            class_nm=self.class_nm,
            academy=self.academy,
            start_dt="2020-03-10",
            end_dt=self.end_dt,
            isa_policy=self.isa_policy,
        )

        response = self.client.delete(
            reverse("lecture_details", kwargs={"pk": wrong_lecture.id})
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrongPayment_LectureDetail_delete(self):
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

    def test_not_exist_LectureDetail_delete(self):
        response = self.client.delete("/lecture/300")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)