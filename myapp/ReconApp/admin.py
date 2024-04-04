from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Reconsiliasi , MissingInvoice

admin.site.register(Reconsiliasi)
admin.site.register(MissingInvoice)
