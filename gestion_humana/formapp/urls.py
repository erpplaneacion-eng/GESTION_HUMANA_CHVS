"""
URLs para la aplicación formapp.
Actualizado para usar la estructura refactorizada de views.
"""
from django.urls import path
from .views.views_public import public_form_view, public_update_view
from .views.views_admin import (
    ApplicantListView,
    ApplicantDetailView,
    applicant_edit_view,
    applicant_delete_view,
    solicitar_correccion_view,
)
from .views.views_reports import (
    download_all_zip,
    download_individual_zip,
)

app_name = 'formapp'

urlpatterns = [
    # Rutas públicas
    path('', public_form_view, name='public_form'),
    path('actualizar-datos/<uuid:token>/', public_update_view, name='public_update'),
    
    # Rutas de administrador
    path('admin/applicants/', ApplicantListView.as_view(), name='applicant_list'),
    path('admin/applicants/<int:pk>/', ApplicantDetailView.as_view(), name='applicant_detail'),
    path('admin/applicants/<int:pk>/edit/', applicant_edit_view, name='applicant_edit'),
    path('admin/applicants/<int:pk>/delete/', applicant_delete_view, name='applicant_delete'),
    path('admin/applicants/<int:pk>/solicitar-correccion/', solicitar_correccion_view, name='solicitar_correccion'),
    
    # Rutas de reportes
    path('admin/download-all/', download_all_zip, name='download_all'),
    path('admin/applicants/<int:pk>/download/', download_individual_zip, name='download_individual'),
]
