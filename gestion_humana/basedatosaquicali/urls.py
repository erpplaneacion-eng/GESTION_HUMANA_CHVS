from django.urls import path
from . import views

app_name = 'basedatosaquicali'

urlpatterns = [
    path('buscar/', views.buscar_historico, name='buscar_historico'),
]
