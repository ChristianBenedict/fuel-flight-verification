# Register your models here.
from django.contrib import admin
from .models import FuelVendor

class FuelVendorAdmin(admin.ModelAdmin):
    list_display = ('Date', 'Flight', 'Dep', 'Arr', 'Reg', 'Uplift_in_Lts', 'Invoice', 'Vendor')
    search_fields = ('Date', 'Flight', 'Dep', 'Arr', 'Reg', 'Uplift_in_Lts', 'Invoice', 'Vendor')
    ordering = ['Date', 'Flight', 'Dep', 'Arr', 'Reg', 'Uplift_in_Lts', 'Invoice', 'Vendor']

admin.site.register(FuelVendor, FuelVendorAdmin)


