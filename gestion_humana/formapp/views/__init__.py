"""
Views package para formapp.
Refactorización de views.py en módulos separados por responsabilidad.
"""

# Importar todas las vistas para mantener compatibilidad con urls.py
from .views_public import public_form_view
from .views_admin import (
    ApplicantListView,
    ApplicantDetailView,
    applicant_edit_view,
    applicant_delete_view,
)
from .views_reports import (
    download_individual_zip,
    download_all_zip,
)

__all__ = [
    # Public views
    'public_form_view',

    # Admin views
    'ApplicantListView',
    'ApplicantDetailView',
    'applicant_edit_view',
    'applicant_delete_view',

    # Report views
    'download_individual_zip',
    'download_all_zip',
]
