import django
from datetime import datetime
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect
from .utils import process_uploaded_file, saveVendorToDatabase
from .utils import get_data_occ, change_data_fuel, reconcile_data_occ_less_than_vendor
from .utils import reconcile_data_occ_equal_vendor, reconcile_data_occ_greater_than_vendor
from ReconApp.models import  Result, DetailResult,MissingInvoiceInVendor


# Create your views here.
def index(request):
    # jangan berikan akses ke halaman ini jika user belum login
    if not request.user.is_authenticated:
        return redirect('login')
    elif request.user.is_authenticated:
         
        context = {}
        missing_data_vendor = [] # List untuk menyimpan data yang tidak sama antara vendor dan occ
        missing_data_occ = [] # List untuk menyimpan data yang tidak sama antara vendor dan occ
        missing_invoice_vendor = [] # List untuk menyimpan invoice yang tidak ada di data occ
        missing_invoice_occ = [] # List untuk menyimpan invoice yang tidak ada di data vendor padahal di occ ada
        successful_invoices = [] # List untuk menyimpan invoice yang berhasil diinputkan ke database
        failed_invoices = [] # List untuk menyimpan invoice yang sudah ada di database
        fuel_vendor = None
        fuel_occ = None
        total_occ = 0
        total_vendor = 0
        total_selisih = 0
        data_start_date = None
        data_end_date = None
        
        if request.method == "POST" :
            # memeriksa validate form
            if 'file' in request.FILES and request.FILES['file'].name.endswith('.xlsx') and request.POST.get("date_of_data") is not None:
                # Mendapatkan file yang diunggah dari form
                uploaded_file = request.FILES["file"]
                # Proses file yang diunggah
                df = process_uploaded_file(uploaded_file, request)
                if df is None:
                    return redirect('index')
                # Menyimpan data dari DataFrame ke database
                fuel_vendor=saveVendorToDatabase(df, request, failed_invoices, successful_invoices)
                data_start_date = request.POST.get("date_of_data")  
                data_end_date=request.POST.get("end_date_data")  
                vendor = request.POST.get("vendor")
                fuel_occ = get_data_occ(data_start_date, data_end_date, vendor)
                total_occ, total_vendor = change_data_fuel(fuel_occ, fuel_vendor)
                total_selisih =   total_occ - total_vendor

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
                                
                result_obj = Result.objects.create(
                    time_of_event=datetime.now(),  
                    data_start_date=data_start_date,
                    data_end_date=data_end_date,
                    total_uplift_in_lts_occ=total_occ,
                    total_uplift_in_lts_ven=total_vendor,
                    total_selisih=total_selisih,
                    fuel_agent=vendor,
                )

                detail_result_objects = []

                if missing_data_vendor and missing_data_occ:
                    for i in range(len(missing_data_vendor)):
                        # Konversi format tanggal dari DD/MM/YYYY ke YYYY-MM-DD untuk tanggal occ
                        date_occ_formatted = datetime.strptime(missing_data_occ[i]["Date"], "%d/%m/%Y").strftime("%Y-%m-%d")

                            # Konversi format tanggal dari YYYY-MM-DD ke YYYY-MM-DD untuk tanggal vendor (jika belum dalam format yang benar)
                        date_ven_formatted = (
                            missing_data_vendor[i].Date.strftime("%Y-%m-%d")
                            if isinstance(missing_data_vendor[i].Date, datetime)
                            else missing_data_vendor[i].Date
                        )

                            # Membuat objek DetailResult dan menghubungkannya dengan Result
                        detail_result_obj = DetailResult(
                            result=result_obj,
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
                            fuel_agent=missing_data_vendor[i].Vendor,
                            selisih=missing_data_occ[i]["Uplift_in_Lts"] - missing_data_vendor[i].Uplift_in_Lts,
                        )
                        detail_result_objects.append(detail_result_obj)

                        # Menyimpan semua objek DetailResult ke database
                    DetailResult.objects.bulk_create(detail_result_objects)                

                missing_invoice_in_vendor_objects=[]
                
                if missing_invoice_vendor:
                    for i in range(len(missing_invoice_vendor)):
                        date_formated = (
                            missing_invoice_vendor[i].Date.strftime("%Y-%m-%d")
                            if isinstance(missing_invoice_vendor[i].Date, datetime)
                            else missing_invoice_vendor[i].Date
                        )
                        
                        # Membuat objek MissingInvoice dan menyimpannya ke database
                        missing_invoice_obj = MissingInvoiceInVendor(
                            result=result_obj,
                            date=date_formated,
                            flight=missing_invoice_vendor[i].Flight,
                            departure=missing_invoice_vendor[i].Dep,
                            arrival=missing_invoice_vendor[i].Arr,
                            registration=missing_invoice_vendor[i].Reg,
                            uplift_in_lts=missing_invoice_vendor[i].Uplift_in_Lts,
                            invoice_no=missing_invoice_vendor[i].Invoice,  
                            fuel_agent=missing_invoice_vendor[i].Vendor,
                        )
                        missing_invoice_in_vendor_objects.append(missing_invoice_obj)                    
                    MissingInvoiceInVendor.objects.bulk_create(missing_invoice_in_vendor_objects)
                            
            return redirect('result') 

        # ambil user yang login
        user = request.user
        context = {
            "page_title": "Home",
            "user": user,
        }
        return render(request, "index.html", context)



            

def login(request):
    # Jika user sudah login, maka arahkan ke halaman index
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            django.contrib.auth.login(request, user)
            return redirect('index')
        else:
            return render(request, "login.html")
    return render(request, "login.html")


def logout(request):
    django.contrib.auth.logout(request)
    return redirect('login')




def handler404(request, exception):
    return render(request, 'error/404.html', status=404)


