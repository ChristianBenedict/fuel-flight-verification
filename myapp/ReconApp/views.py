from django.shortcuts import render
from .models import  Result, DetailResult ,MissingInvoiceInVendor, MissingInvoiceInOcc
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime
from django.template.loader import render_to_string


# Create your views here.
def index(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    
    #ambil data DetailResult dari database dalam rentang tanggal start_date dan end_date
    if start_date and end_date:
        detail_results = DetailResult.objects.filter(
            date_occ__gte=start_date, date_occ__lte=end_date
        )
    # ambil data latest_missing_invoices_in_vendor dari database dalam rentang tanggal start_date dan end_date
        missing_invoices_in_vendor = MissingInvoiceInVendor.objects.filter(
            date__gte=start_date, date__lte=end_date
        )
    # ambil data latest_missing_invoices_in_occ dari database dalam rentang tanggal start_date dan end_date
        missing_invoices_in_occ = MissingInvoiceInOcc.objects.filter(
            date__gte=start_date, date__lte=end_date
        )
        
    elif start_date:
        # ambil data DetailResult dari database yang tanggalnya sama dengan start_date
        detail_results = DetailResult.objects.filter(
            date_occ=start_date
        )
        
        # ambil data latest_missing_invoices_in_vendor dari database yang tanggalnya sama dengan start_date
        missing_invoices_in_vendor = MissingInvoiceInVendor.objects.filter(
            date=start_date
        )
        
        # ambil data latest_missing_invoices_in_occ dari database yang tanggalnya sama dengan start_date
        missing_invoices_in_occ = MissingInvoiceInOcc.objects.filter(
            date=start_date
        )
    else:
        # Mengambil entri terbaru dari model Result
        latest_result = Result.objects.latest('time_of_event')
        # Mengambil detail result yang terkait dengan entri terbaru dari Result
        latest_detail_results = latest_result.detail_results.all()
        try:
            latest_missing_invoices_in_vendor = latest_result.missing_invoices_in_vendor.all()
        except:
            latest_missing_invoices_in_vendor = None    
        # buat total_missing_invoices_in_vendor
        total_missing_invoices_in_vendor = 0
        if latest_missing_invoices_in_vendor:
            for item in latest_missing_invoices_in_vendor:
                total_missing_invoices_in_vendor += item.uplift_in_lts
        try:
            latest_missing_invoices_in_occ = latest_result.missing_invoices_in_occ.all()
        except:
            latest_missing_invoices_in_occ = None  
            
        
    if request.method == "POST" and 'export_history_to_pdf' in request.POST:  
        template_path = 'recon/pdf_history.html' 
        context = {
            'latest_result': latest_result,
            'latest_detail_results': latest_detail_results,
            'latest_missing_invoices_in_vendor': latest_missing_invoices_in_vendor,
            'latest_missing_invoices_in_occ': latest_missing_invoices_in_occ,
            'total_missing_invoices_in_vendor': total_missing_invoices_in_vendor,
        }
            
        # Render template
        html_string = render_to_string(template_path, context)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="data_export.pdf"'
        # Create PDF
        pisa_status = pisa.CreatePDF(html_string, dest=response)
        if pisa_status.err:
            return HttpResponse('Terjadi kesalahan saat membuat PDF: %s' % pisa_status.err)
        return response
    else:  
        context = {
            'latest_result': latest_result,
            'latest_detail_results': latest_detail_results,
            'latest_missing_invoices_in_vendor': latest_missing_invoices_in_vendor,
            'latest_missing_invoices_in_occ': latest_missing_invoices_in_occ,
            'total_missing_invoices_in_vendor': total_missing_invoices_in_vendor,
        }
    
    return render(request, 'recon/index.html', context)






