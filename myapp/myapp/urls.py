
from django.contrib import admin
from django.urls import path, include
from myapp.views import index, login

urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path('login/', login, name='index'),
    path('', index, name='index'),
    path('occ/', include('OCCApp.urls', namespace='OCCApp')),
    path('vendor/', include('VendorApp.urls', namespace='VendorApp')),
    path('recon/', include('ReconApp.urls', namespace='ReconApp')),
]
