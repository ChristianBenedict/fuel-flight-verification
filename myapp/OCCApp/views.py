from django.shortcuts import render
from myapp.utils import get_data_from_sheet,get_from_sheet_by_period
from datetime import datetime
import pandas as pd
from django.core.paginator import Paginator

# Create your views here.
# Create your views here.
def index(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    page_number = request.GET.get('page')
    total_uplift_in_lts = 0

    try:
        if start_date and end_date:
            # Ubah format tanggal dari 'YYYY-MM-DD' ke 'DD/MM/YYYY'
            start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%d/%m/%Y')
            end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%d/%m/%Y')

            # Memanggil fungsi untuk mengambil data dari Google Sheets berdasarkan periode tanggal
            sheet_data_occ = get_from_sheet_by_period('Fuel_Uplift_by_Departure_Station', 'IAA', start_date, end_date)
        else:
            sheet_data_occ = get_data_from_sheet('Fuel_Uplift_by_Departure_Station', 'IAA')

        if not sheet_data_occ:  # Tambahkan pengecekan ini
            return render(request, 'error/no_data.html', {})

        paginator = Paginator(sheet_data_occ, 5)
        page_obj = paginator.get_page(page_number)

        # hitung total uplift in lts
        total_uplift_in_lts = sum(float(row['Uplift_in_Lts']) for row in sheet_data_occ)

        if page_obj is None:
            page_obj = sheet_data_occ
        # ubah tipe data dari kolom Date menjadi datetime
        for row in page_obj:
            row['Date'] = datetime.strptime(row['Date'], '%d/%m/%Y').date()
            
        context = {
            'page_title': 'IAA',
            'Fuels_occ': page_obj,
            'total_uplift_in_lts': total_uplift_in_lts,
        }
        return render(request, 'occ/index.html', context)

    except Exception as e:
        return render(request, 'error/error.html', {'error_message': str(e)})