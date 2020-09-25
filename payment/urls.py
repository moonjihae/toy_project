from django.urls import path
from . import views

urlpatterns = [
    path("", views.PaymentList.as_view()),
    path("<int:pk>", views.PaymentDetail.as_view()),
]
