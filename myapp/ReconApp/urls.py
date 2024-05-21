from django.urls import path
from . import views as recon_views



urlpatterns = [
    path('', recon_views.index, name='index'),
]