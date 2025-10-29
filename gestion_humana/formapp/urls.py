
from django.urls import path
from . import views

app_name = 'formapp'

urlpatterns = [
    path('registro/', views.public_form_view, name='public_form'),
    path('lista/', views.ApplicantListView.as_view(), name='applicant_list'),
    path('detalle/<int:pk>/', views.ApplicantDetailView.as_view(), name='applicant_detail'),
    path('editar/<int:pk>/', views.applicant_edit_view, name='applicant_edit'),
    path('eliminar/<int:pk>/', views.applicant_delete_view, name='applicant_delete'),
]
