# from django.shortcuts import render
# from .models import FuelVendor
# from django.core.paginator import Paginator
# from django.utils.dateparse import parse_date

# # Create your views here.Fuel_vendors
# def index(request):
#     try:
#         page_number = request.GET.get('page')
#         start_date = request.GET.get("start_date")
#         end_date = request.GET.get("end_date")
#         page_obj = None  # Inisialisasi page_obj dengan None di awal

#         # ambil data FuelVendor dari database berdasarkan start_date dan end_date
#         if start_date and end_date:
#             start_date = parse_date(start_date)
#             end_date = parse_date(end_date)
#             if start_date is not None and end_date is not None:
#                 fuel_vendors = FuelVendor.objects.filter(
#                     Date__gte=start_date, Date__lte=end_date)
#             else:
#                 fuel_vendors = FuelVendor.objects.all()
#         else:
#             fuel_vendors = FuelVendor.objects.all()

#         if not fuel_vendors.exists():  # Tambahkan pengecekan ini
#             return render(request, 'error/no_data.html', {})

#         paginator = Paginator(fuel_vendors, 5)

#         if page_number:
#             page_obj = paginator.get_page(page_number)

#         total_uplift_in_lts = sum(fuel_vendor.Uplift_in_Lts for fuel_vendor in fuel_vendors)

#         if not page_obj:
#             page_obj = paginator.get_page(1)  # Atau page_obj = fuel_vendors jika Anda ingin menampilkan semua data

#         context = {
#             'page_title': 'Vendor',
#             "Fuel_vendors": page_obj,
#             'total_uplift_in_lts': total_uplift_in_lts,
#             'start_date': start_date,
#             'end_date': end_date,
#         }
#         return render(request, "vendor/index.html", context)

#     except FuelVendor.DoesNotExist:  # Tangani FuelVendor.DoesNotExist
#         return render(request, 'error/no_data.html', {})

#     except Exception as e:  # Tangani Exception lainnya
#         return render(request, 'error/error.html', {'error_message': str(e)})

from .models import FuelVendor
from django.shortcuts import render
def index(request):
    fuel_vendors = FuelVendor.objects.all()
    total_uplift_in_lts = sum(fuel_vendor.Uplift_in_Lts for fuel_vendor in fuel_vendors)
    

    page_title='Vendor'

    context = {
        'fuel_vendors': fuel_vendors,
        'page_title': page_title,
        'total_uplift_in_lts': total_uplift_in_lts,
    }
    return render(request, 'vendor/fuel_vendor_list.html', context)