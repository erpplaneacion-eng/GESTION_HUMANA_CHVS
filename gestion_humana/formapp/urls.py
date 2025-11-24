"""
URLs para la aplicación formapp.
Actualizado para usar la estructura refactorizada de views.
"""
from django.urls import path

# Importar desde el paquete views refactorizado
from .views import (
    public_form_view,
    ApplicantListView,
    ApplicantDetailView,
    applicant_edit_view,
    applicant_delete_view,
    download_individual_zip,
    download_all_zip,
)

app_name = 'formapp'

urlpatterns = [
    # Vista pública
    path('registro/', public_form_view, name='public_form'),

    # Vistas administrativas
    path('lista/', ApplicantListView.as_view(), name='applicant_list'),
    path('detalle/<int:pk>/', ApplicantDetailView.as_view(), name='applicant_detail'),
    path('editar/<int:pk>/', applicant_edit_view, name='applicant_edit'),
    path('eliminar/<int:pk>/', applicant_delete_view, name='applicant_delete'),

    # Vistas de reportes
    path('descargar/<int:pk>/', download_individual_zip, name='download_individual'),
    path('descargar-todo/', download_all_zip, name='download_all'),
]
