from django.urls import path
from . import views as recon_views

app_name = 'ReconApp'

urlpatterns = [
    path('', recon_views.index, name='index'),
]