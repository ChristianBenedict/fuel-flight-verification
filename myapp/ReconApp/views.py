from django.shortcuts import render
from .models import Reconsiliasi, MissingInvoice
from django.core.paginator import Paginator

# Create your views here.
def index (request):
    # ambil data reconsiliasi data database
    reconsiliasi = Reconsiliasi.objects.all()
    
    # ambil data missing invoice dari database
    missing_invoice = MissingInvoice.objects.all()
    
    total_uplift_in_lts = 0
    total_uplift_in_lts_vendor = 0
    total_missing_lts = 0
    
    
    for row in reconsiliasi:
        total_uplift_in_lts += int(row.uplift_in_lts_occ)
        total_uplift_in_lts_vendor += int(row.uplift_in_lts_ven)
        
    for row in missing_invoice:
        total_missing_lts += int(row.uplift_in_lts)
    
    selisih = total_uplift_in_lts_vendor-total_uplift_in_lts 
     
    context = {
            'page_title': 'Reconsiliasi',
            'Reconsiliasi': reconsiliasi,
            'total_uplift_in_lts': total_uplift_in_lts,
            'total_uplift_in_lts_vendor': total_uplift_in_lts_vendor,
            'MissingInvoice': missing_invoice,
            'total_missing_lts': total_missing_lts,
            'selisih': selisih
        }
     
     
     
     
    return render(request, 'recon/index.html', context)