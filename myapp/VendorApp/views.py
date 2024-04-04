from django.shortcuts import render
from .models import FuelVendor
from ReconApp.models import Reconsiliasi


# Create your views here.Fuel_vendors
def index(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    # ambil data FuelVendor dari database berdasarkan start_date dan end_date
    if start_date and end_date:
        fuel_vendors = FuelVendor.objects.filter(
            Date__gte=start_date, Date__lte=end_date
        )
    else:
        fuel_vendors = FuelVendor.objects.all()
   
    total_uplift_in_lts=0
    for fuel_vendor in fuel_vendors:
        total_uplift_in_lts+=fuel_vendor.Uplift_in_Lts
    
     
    # ambil data reconsiliation dari database
    reconsiliasi = Reconsiliasi.objects.all()
    
    
    context = {
        'page_title': 'Vendor',
        "Fuel_vendors": fuel_vendors,
        "Reconsiliasi": reconsiliasi,
        'total_uplift_in_lts':total_uplift_in_lts,
    }

    return render(request, "vendor/index.html", context)
