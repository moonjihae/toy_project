from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from employment.models import Employment
from user.models import User
from lecture.models import Class 
from django.urls import reverse
import json

class EmpListTest(TestCase):
    url='/employment/'
    def setUp(self):
        self.client=APIClient()                            
        self.emp_data={ 
                'company' : 'test_company',
                'salary' : 2000000,
                'salary_ym' : "2020-09-08",
                'emp_status' : 0
                }
        Class.objects.create(
                             class_nm="test_class",academy="test_academy",
                             start_dt="2021-03-10", end_dt="2021-05-10",
                             isa_policy= 
                                    {
                                    "ctp": 2000000,
                                    "pay_per": 0.2,
                                    "deferm_cnt": 6,
                                    "limit_term": "2022-05-10",
                                    "min_income": 150000
                                    }
                             )       
 
        #클래스도 추가해줘야함..
        class_id=Class.objects.get(class_nm="test_class")
        self.user=User.objects.create(user_nm="testuser", phone="01000000", email="test@testuser.com" ,class_id=class_id)
        user_id=self.user.id
        self.emp_data["user_id"]=user_id
        print(self.emp_data)
        self.response=self.client.post(self.url,self.emp_data,format='json')

    def test_emp_registration(self):
        self.assertEqual(self.response.status_code,status.HTTP_201_CREATED)

    def test_get_emp_list(self):
        response=self.client.get(self.url, format='json')
        self.assertEqual(status.HTTP_200_OK,response.status_code)
        self.assertTrue(len(json.loads(response.content))==Employment.objects.count())