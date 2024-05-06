import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

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
        # Ubah format tanggal dari Google Sheet
        date_obj = datetime.strptime(row_dict['Date'], '%d/%m/%Y')
        if start_date <= date_obj <= end_date:
            rows_as_dicts.append(row_dict)
    return rows_as_dicts