from django.urls import path
from . import views

urlpatterns = [
    path("", views.EmpList.as_view()),
    path("<int:pk>", views.EmpDetail.as_view(), name="emp_details"),
    path("<int:pk>/status", views.EmpStatus.as_view(), name="emp_status"),
]
