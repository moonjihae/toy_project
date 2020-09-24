from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from lecture.models import Class
from django.urls import reverse
import json 


class LectureListTest(TestCase):
    url='/lecture/'
    def setUp(self):
        self.client=APIClient()
        self.lecture_data={
            "class_nm": "test_class",
            "academy": "test_academy",
            "start_dt": "2020-03-10",
            "end_dt": "2020-05-10",
            "isa_policy": 
                 {
                    "ctp": 2000000,
                    "pay_per": 0.2,
                    "deferm_cnt": 6,
                    "limit_term": "2021-05-10",
                    "min_income": 150000
                }
        
        }   
        self.response=self.client.post(self.url,self.lecture_data,format='json')

    def test_lecture_registration(self):
        self.assertEqual(self.response.status_code,status.HTTP_201_CREATED)

    def test_get_lecture_list(self):
        response=self.client.get(self.url, format='json')
        self.assertEqual(status.HTTP_200_OK,response.status_code)
        self.assertTrue(len(json.loads(response.content))==Class.objects.count())


class LectureDetailTest(TestCase):
     def setUp(self):
        self.client = APIClient()
        self.class_nm="test_class"
        self.academy="test_academy"
        self.start_dt="2020-10-10"
        self.end_dt="2020-12-10"
        self.isa_policy={
        
            "ctp": 100031,
            "pay_per": 0.35,
            "deferm_cnt": 5,
            "limit_term": "2022-01-01",
            "min_income": 20000
        }
        self.lecture=Class.objects.create(class_nm=self.class_nm,academy=self.academy,start_dt=self.start_dt,end_dt=self.end_dt,isa_policy=self.isa_policy)
        self.url=reverse("lecture_details", kwargs={"pk":self.lecture.id})


     def test_LectureDetail_can_get_a_lecture(self):
        lecture=Class.objects.get()
        response = self.client.get(
                reverse("lecture_details", kwargs={'pk': lecture.id}),
                    format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertContains(response,lecture.id)
        

     def test_lectureDetail_updte(self):
        response=self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

     def test_LectureDetail_delete(self):
        
        response=self.client.delete(self.url)
        self.assertEqual(response.status_code,status.HTTP_204_NO_CONTENT)
