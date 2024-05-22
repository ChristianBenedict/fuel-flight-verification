
from django.contrib import admin
from django.urls import path, include
from myapp.views import index, login,logout
from ReconApp.views import result as result
from ReconApp.views import index as history

handler404 = 'myapp.views.handler404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path("__reload__/", include("django_browser_reload.urls")),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('', index, name='index'),
    path('result/', result, name='result'),
    path('history/',history, name='history'),
    path('occ/', include('OCCApp.urls', namespace='OCCApp')),
    path('vendor/', include('VendorApp.urls', namespace='VendorApp')),

]
