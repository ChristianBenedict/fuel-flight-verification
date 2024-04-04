from django.shortcuts import render, redirect
from myapp.utils import get_data_from_sheet
from datetime import datetime
from ReconApp.models import Reconsiliasi
import pandas as pd

# Create your views here.
def index (request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    total_uplift_in_lts = 0
    

    sheet_data_occ = get_data_from_sheet('Fuel_Uplift_by_Departure_Station', 'test_occ')


    if sheet_data_occ:
        for row in sheet_data_occ:
            date_obj = datetime.strptime(row['Date'], '%d/%m/%Y').date()
            row['Date'] = date_obj

        if start_date and end_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            sheet_data_occ = [row for row in sheet_data_occ if start_date <= row['Date'] <= end_date]
    
    if sheet_data_occ:
        # Convert data to DataFrame
        df = pd.DataFrame(sheet_data_occ)
        
        # Sort DataFrame by 'Dep' column
        df_sorted = df.sort_values(by='Dep')
        
        # Convert DataFrame back to list of dictionaries
        sheet_data_occ = df_sorted.to_dict('records')
        
        for row in sheet_data_occ:
            total_uplift_in_lts += float(row['Uplift_in_Lts'])
        
        
    # ambil data reconsiliasi data database
    reconsiliasi = Reconsiliasi.objects.all()
    
    context = {
        'page_title': 'OCC',
        'Fuels_occ': sheet_data_occ,
        'total_uplift_in_lts': total_uplift_in_lts,
        'Reconsiliasi': reconsiliasi
    }
    
    
    return render(request, 'occ/index.html',context)