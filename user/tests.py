from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from user.models import User
from lecture.models import Class
from django.urls import reverse
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
        self.response = self.client.post(self.url, self.user_data, format="json")

    def test_user_registration(self):
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_get_user_list(self):

        response = self.client.get(self.url, format="json")
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertTrue(len(json.loads(response.content)) == User.objects.count())


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

    def test_UserDetail_can_get_a_user(self):
        user = User.objects.get()
        response = self.client.get(
            reverse("details", kwargs={"pk": user.id}), format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, user.id)

    def test_UserDetail_update(self):
        response = self.client.patch(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_UserDetail_delete(self):

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
