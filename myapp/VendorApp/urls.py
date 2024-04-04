from django.urls import path
from . import views as vendor_views

app_name = 'VendorApp'

urlpatterns = [
    path('', vendor_views.index, name='index'),
    
]