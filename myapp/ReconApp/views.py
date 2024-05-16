from django.shortcuts import render
from .models import  Result, DetailResult ,MissingInvoiceInVendor, MissingInvoiceInOcc
from django.core.paginator import Paginator
from django.http import HttpResponse
from xhtml2pdf import pisa
from datetime import datetime
from django.template.loader import render_to_string


def index(request):
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")
    fuel_agent = request.GET.get("fuel_agent")
    

    try:
        if start_date or end_date:
            total_selisih_fuel=0
        
            #ambil data DetailResult dari database dalam rentang tanggal start_date dan end_date
            if start_date and end_date:
                latest_detail_results = DetailResult.objects.filter(
                    date_occ__gte=start_date, date_occ__lte=end_date
                )
                
                if fuel_agent:
                    latest_detail_results = latest_detail_results.filter(fuel_agent=fuel_agent)
                #hitung total uplift_in_lts_by_iaa
                total_uplift_in_lts_by_iaa = sum(item.uplift_in_lts_occ for item in latest_detail_results)
                
                #hitung total uplift_in_lts_by_vendor
                total_uplift_in_lts_by_vendor = sum(item.uplift_in_lts_ven for item in latest_detail_results)
                
                total_selisih_fuel =   total_uplift_in_lts_by_iaa -total_uplift_in_lts_by_vendor
                
                # ambil data latest_missing_invoices_in_vendor dari database dalam rentang tanggal start_date dan end_date
                latest_missing_invoices_in_vendor = MissingInvoiceInVendor.objects.filter(
                    date__gte=start_date, date__lte=end_date
                )
                if fuel_agent:
                    latest_missing_invoices_in_vendor = latest_missing_invoices_in_vendor.filter(fuel_agent=fuel_agent)
                # hitung total_missing_invoices_in_vendor
                total_missing_invoices_in_vendor = sum(item.uplift_in_lts for item in latest_missing_invoices_in_vendor)
                
                # ambil data latest_missing_invoices_in_occ dari database dalam rentang tanggal start_date dan end_date
                latest_missing_invoices_in_occ = MissingInvoiceInOcc.objects.filter(
                    date__gte=start_date, date__lte=end_date
                )
                
                if fuel_agent:
                    latest_missing_invoices_in_occ = latest_missing_invoices_in_occ.filter(fuel_agent=fuel_agent)
                # hitung total_missing_invoices_in_occ
                total_missing_invoices_in_occ = sum(item.uplift_in_lts for item in latest_missing_invoices_in_occ)
                
                # ambil data dari result dari database dalam rentang tanggal start_date dan end_date
                latest_result = Result.objects.filter(
                    data_start_date=start_date, data_end_date=end_date
                ) 
            elif start_date and not end_date:
                # ambil data DetailResult dari database yang tanggalnya sama dengan start_date
                latest_detail_results = DetailResult.objects.filter(
                    date_occ=start_date
                )
                
                if fuel_agent:
                    latest_detail_results = latest_detail_results.filter(fuel_agent=fuel_agent)
                #hitung total uplift_in_lts_by_iaa
                total_uplift_in_lts_by_iaa = sum(item.uplift_in_lts_occ for item in latest_detail_results)
                
                #hitung total uplift_in_lts_by_vendor
                total_uplift_in_lts_by_vendor = sum(item.uplift_in_lts_ven for item in latest_detail_results)
                
                total_selisih_fuel =  total_uplift_in_lts_by_iaa - total_uplift_in_lts_by_vendor
                
                # ambil data latest_missing_invoices_in_vendor dari database yang tanggalnya sama dengan start_date
                latest_missing_invoices_in_vendor = MissingInvoiceInVendor.objects.filter(
                    date=start_date
                )
                
                if fuel_agent:
                    latest_missing_invoices_in_vendor = latest_missing_invoices_in_vendor.filter(fuel_agent=fuel_agent)
                # hitung total_missing_invoices_in_vendor
                total_missing_invoices_in_vendor = sum(item.uplift_in_lts for item in latest_missing_invoices_in_vendor)
                
                # ambil data latest_missing_invoices_in_occ dari database yang tanggalnya sama dengan start_date
                latest_missing_invoices_in_occ = MissingInvoiceInOcc.objects.filter(
                    date=start_date
                )
                if fuel_agent:
                    latest_missing_invoices_in_occ = latest_missing_invoices_in_occ.filter(fuel_agent=fuel_agent)
                # hitung total_missing_invoices_in_occ
                total_missing_invoices_in_occ = sum(item.uplift_in_lts for item in latest_missing_invoices_in_occ)          
            #fitur export to pdf
            if request.method == "POST" and 'export_history_to_pdf' in request.POST:  
                template_path = 'recon/pdf_history.html' 
                context = {
                    'page_title': 'History',
                    'total_selisih_fuel': total_selisih_fuel,
                    'latest_detail_results': latest_detail_results,
                    'latest_missing_invoices_in_vendor': latest_missing_invoices_in_vendor,
                    'latest_missing_invoices_in_occ': latest_missing_invoices_in_occ,
                    'total_uplift_in_lts_by_iaa': total_uplift_in_lts_by_iaa,
                    'total_uplift_in_lts_by_vendor': total_uplift_in_lts_by_vendor,
                    'total_missing_invoices_in_vendor': total_missing_invoices_in_vendor,
                    'total_missing_invoices_in_occ': total_missing_invoices_in_occ,
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
                    'page_title': 'History',
                    'Start_date': start_date,
                    'End_date': end_date,
                    'total_selisih_fuel': total_selisih_fuel,
                    'latest_detail_results': latest_detail_results,
                    'latest_missing_invoices_in_vendor': latest_missing_invoices_in_vendor,
                    'latest_missing_invoices_in_occ': latest_missing_invoices_in_occ,
                    'total_uplift_in_lts_by_iaa': total_uplift_in_lts_by_iaa,
                    'total_uplift_in_lts_by_vendor': total_uplift_in_lts_by_vendor,
                    'total_missing_invoices_in_vendor': total_missing_invoices_in_vendor,
                    'total_missing_invoices_in_occ': total_missing_invoices_in_occ,
                }
            return render(request, 'recon/index.html', context)
                    
        else:
            # Mengambil entri terbaru dari model Result
            latest_result = Result.objects.latest('time_of_event')
            # Mengambil detail result yang terkait dengan entri terbaru dari Result
            latest_detail_results = latest_result.detail_results.all()
            try:
                latest_missing_invoices_in_vendor = latest_result.missing_invoices_in_vendor.all()
            except Exception as e:
                latest_missing_invoices_in_vendor = None    
                print("Error retrieving missing invoices in vendor:", e)
            # buat total_missing_invoices_in_vendor
            total_missing_invoices_in_vendor = 0
            if latest_missing_invoices_in_vendor:
                for item in latest_missing_invoices_in_vendor:
                    total_missing_invoices_in_vendor += item.uplift_in_lts
            try:
                latest_missing_invoices_in_occ = latest_result.missing_invoices_in_occ.all()
            except Exception as e:
                latest_missing_invoices_in_occ = None  
                print("Error retrieving missing invoices in OCC:", e)
                
            
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
                    'page_title': 'History',
                    'latest_result': latest_result,
                    'latest_detail_results': latest_detail_results,
                    'latest_missing_invoices_in_vendor': latest_missing_invoices_in_vendor,
                    'latest_missing_invoices_in_occ': latest_missing_invoices_in_occ,
                    'total_missing_invoices_in_vendor': total_missing_invoices_in_vendor,
                }
            
            return render(request, 'recon/index.html', context)
        
    except Result.DoesNotExist:
        return render(request, 'error/no_data.html', {})
    except (MissingInvoiceInVendor.DoesNotExist, MissingInvoiceInOcc.DoesNotExist) as e:
        return render(request, 'error/error.html', {'error_message': str(e)})
    except Exception as e:
        return render(request, 'error/error.html', {'error_message': str(e)})





def result(request):
    try:
        # Mengambil entri terbaru dari model Result
        latest_result = Result.objects.latest('time_of_event')
        # Mengambil detail result yang terkait dengan entri terbaru dari Result
        latest_detail_results = latest_result.detail_results.all()
        try:
            latest_missing_invoices_in_vendor = latest_result.missing_invoices_in_vendor.all()
        except Exception as e:
            latest_missing_invoices_in_vendor = None
            print("Error retrieving missing invoices in vendor:", e)
        
        # buat total_missing_invoices_in_vendor
        total_missing_invoices_in_vendor = 0
        if latest_missing_invoices_in_vendor:
            for item in latest_missing_invoices_in_vendor:
                total_missing_invoices_in_vendor += item.uplift_in_lts
        
        total_missing_invoices_in_occ = 0
        try:
            latest_missing_invoices_in_occ = latest_result.missing_invoices_in_occ.all()
            # total_missing_invoices_in_occ
            if latest_missing_invoices_in_occ:
                for item in latest_missing_invoices_in_occ:
                    total_missing_invoices_in_occ += item.uplift_in_lts
        except Exception as e:
            latest_missing_invoices_in_occ = None
            print("Error retrieving missing invoices in OCC:", e)
        
        if request.method == "POST" and 'export_pdf' in request.POST:  
            template_path = 'topdf.html' 
            context = {
                'latest_result': latest_result,
                'latest_detail_results': latest_detail_results,
                'latest_missing_invoices_in_vendor': latest_missing_invoices_in_vendor,
                'latest_missing_invoices_in_occ': latest_missing_invoices_in_occ,
                'total_missing_invoices_in_vendor': total_missing_invoices_in_vendor,
                'total_missing_invoices_in_occ': total_missing_invoices_in_occ,
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
                'total_missing_invoices_in_occ': total_missing_invoices_in_occ,
            }
        
        return render(request, 'result.html', context)
        # jika detail result tidak ada
    except DetailResult.DoesNotExist:
        return render(request, 'error/no_results.html', {})
    except Result.DoesNotExist:
        return render(request, 'error/no_results.html', {})
    except Exception as e:
        return render(request, 'error/error.html', {'error_message': str(e)})

