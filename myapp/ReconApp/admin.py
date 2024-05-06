from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Result , DetailResult

admin.site.register(Result)
admin.site.register(DetailResult)
