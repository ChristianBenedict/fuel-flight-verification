from django.urls import path
from . import views as occ_views

app_name = 'OCCApp'

urlpatterns = [
    path('', occ_views.index, name='index'),
]