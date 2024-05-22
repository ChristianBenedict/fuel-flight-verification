from myapp.utils import get_data_from_sheet
from django.shortcuts import render
def index(request):
    sheet_data_occ = get_data_from_sheet('Fuel_Uplift_by_Departure_Station', 'IAA')    
    total_uplift_in_lts = sum(float(row['Uplift_in_Lts']) for row in sheet_data_occ)

    page_title='IAA'

    context = {
        'Fuels_occ': sheet_data_occ,
        'page_title': page_title,
        'total_uplift_in_lts': total_uplift_in_lts,
    }
    return render(request, 'occ/fuel_occ_list.html', context)