import re
import django
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from VendorApp.models import FuelVendor
from datetime import datetime
from .utils import get_data_from_sheet_by_date , get_data_from_sheet_by_date_and_end_date
from ReconApp.models import Reconsiliasi, MissingInvoice,MissingInvoiceOcc
import pandas as pd
from django.contrib.auth import authenticate
from django.template.loader import render_to_string




def index(request):
    context = {}

    missing_data_vendor = [] # List untuk menyimpan data yang tidak sama antara vendor dan occ
    missing_data_occ = [] # List untuk menyimpan data yang tidak sama antara vendor dan occ
    missing_invoice_vendor = [] # List untuk menyimpan invoice yang tidak ada di data occ
    missing_invoice_occ = [] # List untuk menyimpan invoice yang tidak ada di data vendor padahal di occ ada

    successful_invoices = [] # List untuk menyimpan invoice yang berhasil diinputkan ke database
    failed_invoices = [] # List untuk menyimpan invoice yang sudah ada di database
    fuel_vendor = None
    fuel_occ = None
    
    if request.method == "POST" :

        # memeriksa validate form
        if 'file' in request.FILES and request.FILES['file'].name.endswith('.xlsx') and request.POST.get("date_of_data") is not None:

            # Mendapatkan file yang diunggah dari form
            uploaded_file = request.FILES["file"]
            
            
            # Proses file yang diunggah
            df = process_uploaded_file(uploaded_file)

            # Menyimpan data dari DataFrame ke database
            fuel_vendor=saveVendorToDatabase(df, request, failed_invoices, successful_invoices)
            

            # Jika form di-submit
            data_start_date = request.POST.get("date_of_data")  # mendapatkan tanggal dari form
            data_end_date=request.POST.get("end_date_data")  
            
                           
            # Mendapatkan data dari Google Sheet
            vendor = request.POST.get("vendor")
            fuel_occ = get_data_occ(data_start_date, data_end_date, vendor)
            
            
            total_occ, total_vendor = change_data_fuel(fuel_occ, fuel_vendor)
            
            total_selisih = total_vendor - total_occ


            if fuel_occ is not None and fuel_vendor is not None:
                # cari panjang data fuel_occ dan fuel_vendor
                len_fuel_occ = len(fuel_occ)
                len_fuel_vendor = len(fuel_vendor)

                # jika panjang data fuel_occ dan fuel_vendor sama,
                
                if len_fuel_occ == len_fuel_vendor:
                    # panggil fungsi reconcile_data_occ_equal_vendor
                    missing_data_vendor, missing_data_occ, missing_invoice_vendor, missing_invoice_occ = reconcile_data_occ_equal_vendor(fuel_occ, fuel_vendor, missing_data_vendor, missing_data_occ, missing_invoice_vendor, missing_invoice_occ)
                        
                elif len_fuel_occ > len_fuel_vendor:
                    # panggil fungsi reconcile_data_occ_greater_than_vendor
                    missing_data_vendor, missing_data_occ, missing_invoice_occ,missing_invoice_vendor = reconcile_data_occ_greater_than_vendor(fuel_occ, fuel_vendor, missing_data_vendor, missing_data_occ, missing_invoice_occ,missing_invoice_vendor)

                elif len_fuel_occ < len_fuel_vendor:                            
                    missing_data_vendor, missing_data_occ, missing_invoice_vendor,missing_invoice_occ = reconcile_data_occ_less_than_vendor(fuel_occ, fuel_vendor, missing_data_vendor, missing_data_occ, missing_invoice_vendor,missing_invoice_occ)                            
                            

            if missing_data_vendor and missing_data_occ:
                for i in range(
                    len(missing_data_vendor)):  # Iterasi melalui daftar missing_data_vendor

                    # Konversi format tanggal dari DD/MM/YYYY ke YYYY-MM-DD untuk tanggal occ
                    date_occ_formatted = datetime.strptime(
                        missing_data_occ[i]["Date"], "%d/%m/%Y").strftime("%Y-%m-%d")

                    # Konversi format tanggal dari YYYY-MM-DD ke YYYY-MM-DD untuk tanggal vendor (jika belum dalam format yang benar)
                    date_ven_formatted = (
                        missing_data_vendor[i].Date.strftime("%Y-%m-%d")
                        if isinstance(missing_data_vendor[i].Date, datetime)
                        else missing_data_vendor[i].Date)

                    # Membuat objek Reconsiliasi dan menyimpannya ke database
                    missing_data_obj = Reconsiliasi(
                        date_occ=date_occ_formatted,
                        flight_occ=missing_data_occ[i]["Flight"],
                        departure_occ=missing_data_occ[i]["Dep"],
                        arrival_occ=missing_data_occ[i]["Arr"],
                        registration_occ=missing_data_occ[i]["Reg"],
                        uplift_in_lts_occ=missing_data_occ[i]["Uplift_in_Lts"],
                        date_ven=date_ven_formatted,
                        flight_ven=missing_data_vendor[i].Flight,
                        departure_ven=missing_data_vendor[i].Dep,
                        arrival_ven=missing_data_vendor[i].Arr,
                        registration_ven=missing_data_vendor[i].Reg,
                        uplift_in_lts_ven=missing_data_vendor[i].Uplift_in_Lts,
                        invoice_no=missing_data_vendor[i].Invoice,
                        vendor=missing_data_vendor[i].Vendor,
                    )
                    missing_data_obj.save()  # Menyimpan objek Reconsiliasi ke database

            if missing_invoice_vendor:
                for i in range(len(missing_invoice_vendor)):
                    date_formated = (
                        missing_invoice_vendor[i].Date.strftime("%Y-%m-%d")
                        if isinstance(missing_invoice_vendor[i].Date, datetime)
                        else missing_invoice_vendor[i].Date
                    )
                    
                    # Membuat objek MissingInvoice dan menyimpannya ke database
                    missing_invoice_obj = MissingInvoice(
                        date=date_formated,
                        flight=missing_invoice_vendor[i].Flight,
                        departure=missing_invoice_vendor[i].Dep,
                        arrival=missing_invoice_vendor[i].Arr,
                        registration=missing_invoice_vendor[i].Reg,
                        uplift_in_lts=missing_invoice_vendor[i].Uplift_in_Lts,
                        invoice_no=missing_invoice_vendor[i].Invoice,  
                        Vendor=missing_invoice_vendor[i].Vendor,
                    )
                    missing_invoice_obj.save()
                    
            if missing_invoice_occ:
                #['“16/02/2024” value has an invalid date format. It must be in YYYY-MM-DD format.']
                for i in range(len(missing_invoice_occ)):
                    # Konversi format tanggal dari DD/MM/YYYY ke YYYY-MM-DD
                    date_formated = datetime.strptime(
                        missing_invoice_occ[i]["Date"], "%d/%m/%Y").strftime("%Y-%m-%d")
                    
                    
                    # Membuat objek MissingInvoice dan menyimpannya ke database
                    missing_invoice_occ_obj = MissingInvoiceOcc(
                        date=date_formated,
                        flight=missing_invoice_occ[i]["Flight"],
                        departure=missing_invoice_occ[i]["Dep"],
                        arrival=missing_invoice_occ[i]["Arr"],
                        registration=missing_invoice_occ[i]["Reg"],
                        uplift_in_lts=missing_invoice_occ[i]["Uplift_in_Lts"],
                        invoice_no=missing_invoice_occ[i]["Invoice"],
                        vendor=missing_invoice_occ[i]["Fuel_Agent"],
                    )
                    missing_invoice_occ_obj.save()

            if successful_invoices:
                successful_invoices_str = [str(invoice) for invoice in successful_invoices]
                messages.success(
                    request, f"Data dengan invoice {', '.join(successful_invoices_str)} berhasil ditambahkan ke database.",
                )
                successful_invoices = []

            if failed_invoices:
                failed_invoices_str = [str(invoice) for invoice in failed_invoices]
                messages.error(
                    request,f"Data dengan invoice {', '.join(failed_invoices_str)} sudah ada di database.",
                )
                failed_invoices = []
            
            if vendor:
                request.session['vendor_name'] = vendor
            if data_start_date and data_end_date:
                request.session['data_start_date'] = data_start_date
                request.session['data_end_date'] = data_end_date
            
            if total_vendor :
                request.session['total_vendor'] = total_vendor
            if total_occ:
                request.session['total_occ'] = total_occ
            
            if total_selisih:
                request.session['total_selisih'] = total_selisih
                
            # Mengonversi objek FuelVendor menjadi dICTIONARY
            if missing_data_vendor and missing_data_occ:
                missing_data_vendor_dicts = [to_dict(item) for item in missing_data_vendor]
                missing_data_occ_dicts = [to_dict_occ(item) for item in missing_data_occ]
            
                request.session['missing_data_occ'] = missing_data_occ_dicts
                request.session['missing_data_vendor'] = missing_data_vendor_dicts
                
            if missing_invoice_vendor:
                missing_invoice_vendor_dicts = [to_dict(item) for item in missing_invoice_vendor]
                total_missing_invoice_vendor = sum(item["Uplift_in_Lts"] for item in missing_invoice_vendor_dicts)
                request.session['total_missing_invoice_vendor'] = total_missing_invoice_vendor
                request.session['missing_invoice_vendor'] = missing_invoice_vendor_dicts

            if missing_invoice_occ:
                missing_invoice_occ_dicts = [to_dict_occ(item) for item in missing_invoice_occ]
                # ambil total Uplift_in_Lts pada missing invoice vendor
                total_missing_invoice_occ = sum(item["Uplift_in_Lts"] for item in missing_invoice_occ)
                request.session['total_missing_invoice_occ'] = total_missing_invoice_occ
                request.session['missing_invoice_occ'] = missing_invoice_occ_dicts
            
            
             
        return redirect('result') 


    # ambil data dari database Reconsiliasi
    reconsiliasi = Reconsiliasi.objects.all()

    context = {
        "page_title": "Home",
        "Reconsiliasi": reconsiliasi,
        }
    
    return render(request, "index.html", context)







            
def process_uploaded_file(uploaded_file):
    """Proses file yang diunggah dan kembalikan DataFrame."""
    ##df = pd.read_excel(uploaded_file)
    ##df = pd.read_excel(uploaded_file, dtype={'Invoice': str}) 
    df = pd.read_excel(uploaded_file, dtype='str') 
    columns_to_keep = ["Date", "Flight", "Dep", "Arr", "Reg", "Uplift_in_Lts", "Invoice"]
    df = df[columns_to_keep]
    df.columns = ["Date", "Flight", "Dep", "Arr", "Reg", "Uplift_in_Lts", "Invoice"]
        
    # Pembersihan data untuk berbagai format tanggal
    for index, row in df.iterrows():
        date_str = str(row['Date'])  # Konversi ke string untuk memastikan
        # Contoh pembersihan untuk format 'YYYY-MM-DD 00:00:00'
        if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_str):
            date_str = date_str.split()[0]  # Ambil bagian pertama
        # Contoh pembersihan untuk format 'YYYY/MM/DD'
        elif re.match(r'\d{4}/\d{2}/\d{2}', date_str):
            date_str = date_str.replace('/', '-')  # Ganti '/' dengan '-'
        # Anda dapat menambahkan penanganan khusus untuk format lain di sini

        # Update nilai di data frame
        df.at[index, 'Date'] = date_str
        
        
        # Konversi kolom 'Date' ke tipe data datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')   
        
   
    return df
        
        
        
            
def saveVendorToDatabase(df, request, failed_invoices, successful_invoices):
    """Menyimpan data dari DataFrame ke database."""
    fuel_vendor_list = []
    # Menyimpan data ke database
    for index, row in df.iterrows():
        # ambil vendor dari request.POST
        vendor = request.POST.get("vendor")
        fuel_vendor = FuelVendor(
            Date=row["Date"],
            Flight=row["Flight"],
            Dep=row["Dep"],
            Arr=row["Arr"],
            Reg=row["Reg"],
            Uplift_in_Lts=float(row["Uplift_in_Lts"]),
            Invoice=str(row["Invoice"]),
            Vendor=vendor,
        )  # Membuat objek FuelVendor


        # sebelum menyimpan data, cek apakah data sudah ada di database, cek berdasarkan Invoice
        if FuelVendor.objects.filter(Invoice=row["Invoice"]).exists():
            failed_invoices.append(row["Invoice"])
        else:
            fuel_vendor_list.append(fuel_vendor)
            successful_invoices.append(row["Invoice"])
    # Menyimpan semua objek fuel_vendor dalam satu transaksi
    FuelVendor.objects.bulk_create(fuel_vendor_list)
    return fuel_vendor_list

            
    
    
def change_data_fuel(fuel_occ, fuel_vendor):
    for i in range(len(fuel_occ)):
        # ubah tipe data Uplift_in_Lts dari string ke float
        fuel_occ[i]["Uplift_in_Lts"] = float(fuel_occ[i]["Uplift_in_Lts"])
        
        
        # ambil total Uplift_in_Lts by occ
        total_occ = sum(float(item["Uplift_in_Lts"]) for item in fuel_occ)
        
        
        
        
    for i in range(len(fuel_vendor)):
        # ubah tipe data Uplift_in_Lts dari string ke float
        fuel_vendor[i].Uplift_in_Lts = float(fuel_vendor[i].Uplift_in_Lts)
        
        # print semua data  Uplift_in_Lts by vendor
        
        # ambil total Uplift_in_Lts by vendor
        total_vendor = sum(item.Uplift_in_Lts for item in fuel_vendor)
        
    return total_occ, total_vendor
    
        

    

def get_data_occ(data_start_date, data_end_date, vendor):
    vendor_name = vendor
    if data_start_date:
        if data_end_date:
            formatted_date = datetime.strptime(data_start_date, "%Y-%m-%d").strftime("%d/%m/%Y")
            formatted_end_date = datetime.strptime(data_end_date, "%Y-%m-%d").strftime("%d/%m/%Y")
            fuel_occ = get_data_from_sheet_by_date_and_end_date(
                "Fuel_Uplift_by_Departure_Station", "test_occ", formatted_date, formatted_end_date,vendor_name)
            return fuel_occ
        else:
            formatted_date = datetime.strptime(data_start_date, "%Y-%m-%d").strftime("%d/%m/%Y")
            fuel_occ = get_data_from_sheet_by_date(
                "Fuel_Uplift_by_Departure_Station", "test_occ", formatted_date,vendor_name )
            return fuel_occ
    else:
        return None
    
    


                    
# Fungsi rekonsiliasi data jika len_fuel_occ < len_fuel_vendor
def reconcile_data_occ_less_than_vendor(fuel_occ, fuel_vendor, missing_data_vendor, missing_data_occ, missing_invoice_vendor, missing_invoice_occ):
    # Mengambil set Invoice dari fuel_occ
    fuel_occ_invoices = set(item["Invoice"] for item in fuel_occ)

    for vendor_item in fuel_vendor:
        if vendor_item.Invoice in fuel_occ_invoices:
            # Jika Invoice ada di fuel_occ, bandingkan data
            occ_item = next((item for item in fuel_occ if item["Invoice"] == vendor_item.Invoice), None)
            if occ_item and occ_item["Uplift_in_Lts"] != vendor_item.Uplift_in_Lts:
                missing_data_vendor.append(vendor_item)
                missing_data_occ.append(occ_item)
        else:
            # Jika Invoice tidak ada di fuel_occ, tambahkan ke missing_invoice_vendor
            missing_invoice_vendor.append(vendor_item)

    # Temukan invoice yang ada di fuel_occ tetapi tidak ada di fuel_vendor
    missing_invoices_occ = fuel_occ_invoices - set(item.Invoice for item in fuel_vendor)
    # Ambil detail invoice yang hilang dari fuel_occ
    missing_invoice_occ.extend(item for item in fuel_occ if item["Invoice"] in missing_invoices_occ)

    return missing_data_vendor, missing_data_occ, missing_invoice_vendor, missing_invoice_occ

              
            
            
# fungsi rekonsiliasi data jika len_fuel_occ dan len_fuel_vendor sama
def reconcile_data_occ_equal_vendor(fuel_occ, fuel_vendor, missing_data_vendor, missing_data_occ, missing_invoice_vendor, missing_invoice_occ):
    # Ambil set invoice untuk fuel_occ dan fuel_vendor
    fuel_occ_invoices = set(item["Invoice"] for item in fuel_occ)
    fuel_vendor_invoices = set(item.Invoice for item in fuel_vendor)

    # Temukan invoice yang ada di fuel_occ tetapi tidak ada di fuel_vendor
    missing_invoices_vendor = fuel_occ_invoices - fuel_vendor_invoices

    # Temukan invoice yang ada di fuel_vendor tetapi tidak ada di fuel_occ
    missing_invoices_occ = fuel_vendor_invoices - fuel_occ_invoices

    # Masukkan missing invoices ke dalam list masing-masing
    missing_invoice_occ = [item for item in fuel_occ if item["Invoice"] in missing_invoices_occ]
    missing_invoice_vendor = [item for item in fuel_vendor if item.Invoice in missing_invoices_vendor]

    # Lakukan iterasi melalui set invoice yang ada di fuel_occ_invoices
    for invoice in fuel_occ_invoices:
        # Jika invoice ada di fuel_vendor_invoices
        if invoice in fuel_vendor_invoices:
            # Bandingkan data
            occ_item = next((item for item in fuel_occ if item["Invoice"] == invoice), None)
            vendor_item = next((item for item in fuel_vendor if item.Invoice == invoice), None)
            if occ_item and vendor_item and occ_item["Uplift_in_Lts"] != vendor_item.Uplift_in_Lts:
                # Jika data tidak sama, masukkan ke dalam list missing_data
                missing_data_vendor.append(vendor_item)
                missing_data_occ.append(occ_item)
        else:
            # Jika invoice tidak ada di fuel_vendor, masukkan ke dalam list missing_invoice
            missing_invoice_occ.append(next((item for item in fuel_occ if item["Invoice"] == invoice), None))

    # Jika ada invoice yang ada di fuel_vendor tetapi tidak ada di fuel_occ
    for invoice in missing_invoices_occ:
        missing_invoice_vendor.append(next((item for item in fuel_vendor if item.Invoice == invoice), None))
    
    return missing_data_vendor, missing_data_occ, missing_invoice_vendor, missing_invoice_occ



# Fungsi rekonsiliasi data jika len_fuel_occ > len_fuel_vendor
def reconcile_data_occ_greater_than_vendor(fuel_occ, fuel_vendor, missing_data_vendor, missing_data_occ, missing_invoices_occ, missing_invoice_vendor):
    # Mengambil set Invoice dari fuel_vendor
    fuel_vendor_invoices = set(item.Invoice for item in fuel_vendor)
    
    for occ_item in fuel_occ:
        if occ_item["Invoice"] in fuel_vendor_invoices:
            # Jika Invoice ada di fuel_vendor, bandingkan data
            vendor_item = next((item for item in fuel_vendor if item.Invoice == occ_item["Invoice"]), None)
            if vendor_item and occ_item["Uplift_in_Lts"] != vendor_item.Uplift_in_Lts:
                missing_data_vendor.append(vendor_item)
                missing_data_occ.append(occ_item)
        else:
            # Jika Invoice tidak ada di fuel_vendor, tambahkan ke missing_invoices_occ
            missing_invoices_occ.append(occ_item)

    # Temukan invoice yang ada di fuel_vendor tetapi tidak ada di fuel_occ
    missing_invoices_vendor = fuel_vendor_invoices - set(item["Invoice"] for item in fuel_occ)
    # Ambil detail invoice yang hilang dari fuel_vendor
    missing_invoice_vendor.extend(item for item in fuel_vendor if item.Invoice in missing_invoices_vendor)

    return missing_data_vendor, missing_data_occ, missing_invoices_occ, missing_invoice_vendor




def login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        print(user)
        if user is not None:
            django.contrib.auth.login(request, user)
            return render(request, "index.html")
        else:
            return render(request, "login.html")
    return render(request, "login.html")






from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa


from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib import messages
from datetime import datetime


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
                print('masuk coy')
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
                request.session.flush()
                return response
            else:
                print('salah masuk')
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




def to_dict(instance):
    return {
        'Date': str(instance.Date),
        'Flight': instance.Flight,
        'Dep': instance.Dep,
        'Arr': instance.Arr,
        'Reg': instance.Reg,
        'Uplift_in_Lts': instance.Uplift_in_Lts,
        'Invoice': instance.Invoice,
        'Vendor': instance.Vendor,
    }
    

def to_dict_occ(data_dict):
    return {
        'Date': data_dict["Date"],
        'Flight': data_dict["Flight"],
        'Dep': data_dict["Dep"],
        'Arr': data_dict["Arr"],
        'Reg': data_dict["Reg"],
        'Uplift_in_Lts': data_dict["Uplift_in_Lts"],
        'Invoice': data_dict["Invoice"],
        'Fuel_Agent': data_dict["Fuel_Agent"],
    }
    

def test(request):
    return render(request, 'test.html')
