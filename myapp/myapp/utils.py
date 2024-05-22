
import re
import gspread
import pandas as pd
from datetime import datetime
from django.contrib import messages
from VendorApp.models import FuelVendor
from oauth2client.service_account import ServiceAccountCredentials




def get_credentials():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('static/credentials/ffv-iaa-a22ac4b392e9.json', scope)
    return creds


def get_data_from_sheet(sheet_name, worksheet_name):
    creds = get_credentials()
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).worksheet(worksheet_name)
    data = sheet.get_all_values()
    headers = data[0]
    rows = data[1:]
    rows_as_dicts = []
    for row in rows:
        row_dict = dict(zip(headers, row))
        rows_as_dicts.append(row_dict)
    return rows_as_dicts


# fungsi mengambil data dari sheet  berdasarkan tanggal yang diinput
def get_data_from_sheet_by_date(sheet_name, worksheet_name, date,fuel_agent):
    creds = get_credentials()
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).worksheet(worksheet_name)
    data = sheet.get_all_values()
    headers = data[0]
    rows = data[1:]
    rows_as_dicts = []
    for row in rows:
        row_dict = dict(zip(headers, row))
        # Ubah format tanggal dari Google Sheet
        date_obj = row_dict['Date']
        if date_obj == date:
            if fuel_agent.lower() in row_dict['Fuel_Agent'].lower():
                rows_as_dicts.append(row_dict)
    return rows_as_dicts


# get_data_from_sheet_by_date_and_end_date fungsi mengambil data dari sheet dalam rentang tanggal yang diinput yaitu start_date dan end_date
def get_data_from_sheet_by_date_and_end_date(sheet_name, worksheet_name, start_date_str, end_date_str, fuel_agent):
    start_date = datetime.strptime(start_date_str, '%d/%m/%Y')  # Konversi string ke objek datetime
    end_date = datetime.strptime(end_date_str, '%d/%m/%Y')      # Konversi string ke objek datetime
    
    creds = get_credentials()
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).worksheet(worksheet_name)
    data = sheet.get_all_values()
    headers = data[0]
    rows = data[1:]
    rows_as_dicts = []
    for row in rows:
        row_dict = dict(zip(headers, row))
        # Ubah format tanggal dari Google Sheet
        date_obj = datetime.strptime(row_dict['Date'], '%d/%m/%Y')
        if start_date <= date_obj <= end_date:
            if fuel_agent.lower() in row_dict['Fuel_Agent'].lower():
                rows_as_dicts.append(row_dict)
    return rows_as_dicts


def get_from_sheet_by_period(sheet_name, worksheet_name, start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, '%d/%m/%Y')  # Konversi string ke objek datetime
    end_date = datetime.strptime(end_date_str, '%d/%m/%Y')      # Konversi string ke objek datetime
    creds = get_credentials()
    client = gspread.authorize(creds)
    sheet = client.open(sheet_name).worksheet(worksheet_name)
    data = sheet.get_all_values()
    headers = data[0]
    rows = data[1:]
    rows_as_dicts = []
    
    for row in rows:
        row_dict = dict(zip(headers, row))
        # Periksa apakah 'Date' tidak kosong atau tidak null
        if row_dict['Date'] and row_dict['Date'].strip():
            # Ubah tipe data dari kolom 'Date' menjadi datetime
            date_obj = datetime.strptime(row_dict['Date'], '%d/%m/%Y')
            if start_date <= date_obj <= end_date:
                rows_as_dicts.append(row_dict)
        else:
            # Lakukan sesuatu jika 'Date' kosong atau null (opsional)
            pass 
    return rows_as_dicts



def get_data_occ(data_start_date, data_end_date, vendor):
    vendor_name = vendor
    if data_start_date:
        if data_end_date:
            formatted_date = datetime.strptime(data_start_date, "%Y-%m-%d").strftime("%d/%m/%Y")
            formatted_end_date = datetime.strptime(data_end_date, "%Y-%m-%d").strftime("%d/%m/%Y")
            fuel_occ = get_data_from_sheet_by_date_and_end_date(
                "Fuel_Uplift_by_Departure_Station", "IAA", formatted_date, formatted_end_date,vendor_name)
            return fuel_occ
        else:
            formatted_date = datetime.strptime(data_start_date, "%Y-%m-%d").strftime("%d/%m/%Y")
            fuel_occ = get_data_from_sheet_by_date(
                "Fuel_Uplift_by_Departure_Station", "IAA", formatted_date,vendor_name )
            return fuel_occ
    else:
        return None

    
    
    
def change_data_fuel(fuel_occ, fuel_vendor):
    total_occ = 0
    total_vendor = 0
    # Buat set untuk menyimpan invoice dari fuel_vendor
    vendor_invoices = {vendor.Invoice for vendor in fuel_vendor}
    # Ubah tipe data Uplift_in_Lts menjadi float dan jumlahkan hanya jika invoice ada di vendor_invoices
    for i in range(len(fuel_occ)):
        fuel_occ[i]["Invoice"] = fuel_occ[i]["Invoice"].strip()
        fuel_occ[i]["Uplift_in_Lts"] = float(fuel_occ[i]["Uplift_in_Lts"])
        if fuel_occ[i]["Invoice"] in vendor_invoices:
            total_occ += fuel_occ[i]["Uplift_in_Lts"]
    # Ubah tipe data Uplift_in_Lts menjadi float dan jumlahkan semua Uplift_in_Lts dari fuel_vendor
    for i in range(len(fuel_vendor)):
        fuel_vendor[i].Invoice = fuel_vendor[i].Invoice.strip()
        fuel_vendor[i].Uplift_in_Lts = float(fuel_vendor[i].Uplift_in_Lts)
        total_vendor += fuel_vendor[i].Uplift_in_Lts

    return total_occ, total_vendor


def to_dict(instance): # ini berguna untuk mengubah data dari instance menjadi dictionary
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
    


def to_dict_occ(data_dict): # ini berguna untuk mengubah data dari instance menjadi dictionary
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
    
    
    
            
def process_uploaded_file(uploaded_file, request):
    try:
        df = pd.read_excel(uploaded_file, dtype='str') 
    except Exception as e:
        raise ValueError("Gagal membaca file Excel: " + str(e))
        
    required_columns = ["Date", "Flight", "Dep", "Arr", "Reg", "Uplift_in_Lts", "Invoice"]
    
    # Memeriksa apakah semua kolom yang diperlukan ada dalam dataframe
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        messages.error(request, "Pastikan Semua Atribut Berikut Ada Pada File Excel: " + ', '.join(missing_columns))
        return None
        
    df = df[required_columns]
    df.columns = ["Date", "Flight", "Dep", "Arr", "Reg", "Uplift_in_Lts", "Invoice"]

    # cek apakah kolo 'Date' sudah memiliki tipe data datetime
    for index, row in df.iterrows():
        if  isinstance(row['Date'], datetime):
            print('yes')
            continue
        else:
            # print date yang tidak sesuai format
            date_str = str(row['Date'])  # Konversi ke string untuk memastikan
            # Contoh pembersihan untuk format 'YYYY-MM-DD 00:00:00'
            if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', date_str):
                date_str = date_str.split()[0]  # Ambil bagian pertama 2024-02-06
                #buat kondisi jika format tanggal adalah '2024-02-06', maka ubah ke  06/02/2024
                if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                    date_str = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                elif re.match(r'\d{2}-\d{2}-\d{4}', date_str):
                    date_str = datetime.strptime(date_str, "%d-%m-%Y").strftime("%d/%m/%Y")
                elif re.match(r'\d{2}/\d{2}/\d{4}', date_str):
                    date_str = date_str
            # Contoh pembersihan untuk format 'YYYY/MM/DD'
            elif re.match(r'\d{4}/\d{2}/\d{2}', date_str):
                date_str = date_str.replace('/', '-')  # Ganti '/' dengan '-'
            elif re.match(r'\d{2}/\d{2}/\d{4}', date_str):
                date_str = datetime.strptime(date_str, "%d/%m/%Y").strftime("%d/%m/%Y")
            else:
                # jika format tanggal tidak sesuai, maka berikan pesan error
                messages.error(request, f"Format tanggal tidak valid: {date_str}")
            # Update nilai di data frame
            df.at[index, 'Date'] = date_str
    # Konversi kolom 'Date' ke tipe data datetime
    # df['Date'] = pd.to_datetime(df['Date'], errors='coerce')  
    df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')
    return df



            
def saveVendorToDatabase(df, request, failed_invoices, successful_invoices):
    new_invoices=[]
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
            new_invoices.append(fuel_vendor)
        else:
            fuel_vendor_list.append(fuel_vendor)
            new_invoices.append(fuel_vendor)
            successful_invoices.append(row["Invoice"])
    # Menyimpan semua objek fuel_vendor dalam satu transaksi
    FuelVendor.objects.bulk_create(fuel_vendor_list)
    return new_invoices


                    
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




