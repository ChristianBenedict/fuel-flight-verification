from django.shortcuts import render
from .models import Reconsiliasi, MissingInvoice
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

# Create your views here.
def index (request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    
    if start_date and end_date:
        reconsiliasi = Reconsiliasi.objects.filter(
            date_occ__gte=start_date, date_occ__lte=end_date
        )
        missing_invoice = MissingInvoice.objects.filter(
            date__gte=start_date, date__lte=end_date
        )
    elif start_date:
        # ambil data reconsiliation dari database yang tanggalnya sama dengan start_date
        reconsiliasi = Reconsiliasi.objects.filter(
            date_occ=start_date
        )
        # ambil data missing invoice dari database yang tanggalnya sama dengan start_date
        missing_invoice = MissingInvoice.objects.filter(
            date=start_date
        )
    else:    
        # jika date_of_data dan end_date_data adalah none
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
    
    total_selisih = total_uplift_in_lts_vendor-total_uplift_in_lts 
    
    # selisih 
    for row in reconsiliasi:
        row.selisih = int(row.uplift_in_lts_ven) - int(row.uplift_in_lts_occ)
    
    #export to pdf
    
    if request.method=='POST' and 'export_history_to_pdf' in request.POST:
        print('export to pdfco ')
        template_path = 'recon/pdf_history.html'
        context = {
            'Reconsiliasi': reconsiliasi,
            'total_uplift_in_lts': total_uplift_in_lts,
            'total_uplift_in_lts_vendor': total_uplift_in_lts_vendor,
            'MissingInvoice': missing_invoice,
            'total_missing_lts': total_missing_lts,
            'total_selisih': total_selisih
            
        }
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="historical_data.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
    else:
        context = {
                'page_title': 'Historical Data',
                'Reconsiliasi': reconsiliasi,
                'total_uplift_in_lts': total_uplift_in_lts,
                'total_uplift_in_lts_vendor': total_uplift_in_lts_vendor,
                'MissingInvoice': missing_invoice,
                'total_missing_lts': total_missing_lts,
                'total_selisih': total_selisih
            }
     
     
    return render(request, 'recon/index.html', context)




# fungsi mengambil nilai date_of_data dan end_date_of_data  views myapp
