
from django.urls import path
from . import views

app_name = 'formapp'

urlpatterns = [
    path('registro/', views.public_form_view, name='public_form'),
    path('lista/', views.ApplicantListView.as_view(), name='applicant_list'),
    path('detalle/<int:pk>/', views.ApplicantDetailView.as_view(), name='applicant_detail'),
]
