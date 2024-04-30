from django.shortcuts import render
from .models import FuelVendor
from ReconApp.models import Reconsiliasi
from django.core.paginator import Paginator

# Create your views here.Fuel_vendors
def index(request):
    page_number = request.GET.get('page')
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    # ambil data FuelVendor dari database berdasarkan start_date dan end_date
    if start_date and end_date:
        fuel_vendors = FuelVendor.objects.filter(
            Date__gte=start_date, Date__lte=end_date
        )
        
    else:
        fuel_vendors = FuelVendor.objects.all()
    
    paginator = Paginator(fuel_vendors, 5)
    page_obj = paginator.get_page(page_number)
        
        
    total_uplift_in_lts=0
    for fuel_vendor in fuel_vendors:
        total_uplift_in_lts+=fuel_vendor.Uplift_in_Lts
    
     
    # ambil data reconsiliation dari database
    reconsiliasi = Reconsiliasi.objects.all()
    
    
    context = {
        'page_title': 'Vendor',
        "Fuel_vendors": page_obj,
        "Reconsiliasi": reconsiliasi,
        'total_uplift_in_lts':total_uplift_in_lts,
        'start_date': start_date,
        'end_date': end_date,
    }

    return render(request, "vendor/index.html", context)
