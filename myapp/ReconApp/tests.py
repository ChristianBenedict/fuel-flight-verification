def result(request):

    try:
        vendor_name = request.session.get('vendor_name', None)
        data_start_date = request.session.get('data_start_date', None)
        data_end_date = request.session.get('data_end_date', None)
        missing_data_vendor = request.session.get('missing_data_vendor', [])
        missing_data_occ = request.session.get('missing_data_occ', [])
        total_vendor = request.session.get('total_vendor', 0)
        total_occ = request.session.get('total_occ', 0)
        missing_invoice_vendor = request.session.get('missing_invoice_vendor', [])

        for item in missing_invoice_vendor:
            try:
                item["Date"] = datetime.strptime(item['Date'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                messages.error(request, f"Format tanggal '{item['Date']}' tidak valid.")

        total_selisih = request.session.get('total_selisih', 0)
        data_start_date = datetime.strptime(data_start_date, '%Y-%m-%d')
        data_end_date = datetime.strptime(data_end_date, '%Y-%m-%d')
        total_missing_invoice_vendor = request.session.get('total_missing_invoice_vendor', 0)
        total_missing_invoice_vendor = int(total_missing_invoice_vendor)

        selisih_list = []
        for occ, vendor in zip(missing_data_occ, missing_data_vendor):
            try:
                uplift_occ = float(occ["Uplift_in_Lts"])
                uplift_vendor = float(vendor["Uplift_in_Lts"])
                selisih_list.append(uplift_occ - uplift_vendor)
            except ValueError:
                messages.error(request, f"Nilai 'Uplift_in_Lts' tidak valid untuk OCC: {occ} dan Vendor: {vendor}")

        if request.method == 'POST' and 'export_pdf' in request.POST:
            zipped_data = zip(request.session.get('missing_data_occ', []), request.session.get('missing_data_vendor', []), selisih_list)
            html_string = render_to_string('topdf.html', {
                'zipped_data': zipped_data,
                'total_vendor': total_vendor,
                'total_occ': total_occ,
                'total_selisih': total_selisih,
                'Vendor_name': vendor_name,
                'Data_start_date': data_start_date,
                'Data_end_date': data_end_date,
                'missing_invoice_vendor': missing_invoice_vendor,
                'total_missing_invoice_vendor': total_missing_invoice_vendor,
            })

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="data_export.pdf"'

            pisa_status = pisa.CreatePDF(html_string, dest=response)

            if pisa_status.err:
                return HttpResponse('Terjadi kesalahan saat membuat PDF: %s' % pisa_status.err)
            return response

        else:
            if missing_data_vendor and missing_data_occ:
                context = {
                    'page_title': 'Result',
                    'zipped_data': zip(missing_data_occ, missing_data_vendor, selisih_list),
                    'total_vendor': total_vendor,
                    'total_occ': total_occ,
                    'total_selisih': total_selisih,
                    'Vendor_name': vendor_name,
                    'Data_start_date': data_start_date,
                    'Data_end_date': data_end_date,
                    'missing_invoice_vendor': missing_invoice_vendor,
                    'total_missing_invoice_vendor': total_missing_invoice_vendor,
                }
                response = render(request, 'result.html', context)
                return response
            else:
                return render(request, 'no_results.html')

    except KeyError as e:
        messages.error(request, f"Kunci '{e.args[0]}' tidak ditemukan dalam session.")
        return render(request, 'no_results.html', {})  # Kembalikan respons dengan template kosong
    except ObjectDoesNotExist as e:
        messages.error(request, str(e))
        return render(request, 'no_results.html', {})  # Kembalikan respons dengan template kosong
    except ValidationError as e:
        messages.error(request, str(e))
        return render(request, 'no_results.html', {})  # Kembalikan respons dengan template kosong
    except Exception as e:
        messages.error(request, str(e))
        return render(request, 'no_results.html', {})  # Kembalikan respons dengan template kosong







from django.shortcuts import render
from .models import Reconsiliasi, MissingInvoice
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from datetime import datetime

# Create your views here.
def index(request):
    try:
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

        if not reconsiliasi.exists() and not missing_invoice.exists():
            return render(request, 'recon/noresult.html')

        total_uplift_in_lts = 0
        total_uplift_in_lts_vendor = 0
        total_missing_lts = 0

        for row in reconsiliasi:
            total_uplift_in_lts += int(row.uplift_in_lts_occ)
            total_uplift_in_lts_vendor += int(row.uplift_in_lts_ven)

        for row in missing_invoice:
            total_missing_lts += int(row.uplift_in_lts)

        total_selisih = total_uplift_in_lts_vendor - total_uplift_in_lts

        # selisih
        for row in reconsiliasi:
            row.selisih = int(row.uplift_in_lts_ven) - int(row.uplift_in_lts_occ)

        # export to pdf

        # ubah tipe data dari  start_date dan end_date menjadi datetime
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        if request.method == 'POST' and 'export_history_to_pdf' in request.POST:
            print('export to pdfco ')
            template_path = 'recon/pdf_history.html'
            context = {
                'Reconsiliasi': reconsiliasi,
                'total_uplift_in_lts': total_uplift_in_lts,
                'total_uplift_in_lts_vendor': total_uplift_in_lts_vendor,
                'MissingInvoice': missing_invoice,
                'total_missing_lts': total_missing_lts,
                'total_selisih': total_selisih,
                'Start_date': start_date,
                'End_date': end_date,

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
                'total_selisih': total_selisih,
                'Start_date': start_date,
                'End_date': end_date,
            }

        return render(request, 'recon/index.html', context)

    except Exception as e:
        # Handle the exception here
        return render(request, 'recon/error.html', {'error_message': str(e)})








def result(request):
    try:
        # Mengambil entri terbaru dari model Result
        latest_result = Result.objects.latest('time_of_event')
        # Mengambil detail result yang terkait dengan entri terbaru dari Result
        latest_detail_results = latest_result.detail_results.all()
        
        try:
            latest_missing_invoices_in_vendor = latest_result.missing_invoices_in_vendor.all()
        except Exception as vendor_error:
            latest_missing_invoices_in_vendor = None    
        
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
        except Exception as occ_error:
            latest_missing_invoices_in_occ = None

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
    
    except Exception as error:
        # Tangani kesalahan secara umum
        return HttpResponse(f'Terjadi kesalahan: {error}')
