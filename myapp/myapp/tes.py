import django
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from VendorApp.models import FuelVendor
from OCCApp.models import FuelOcc
from datetime import datetime
from .utils import get_data_from_sheet_by_date
from ReconApp.models import Reconsiliasi, MissingInvoice
import pandas as pd
from django.contrib.auth import authenticate


def process_uploaded_file(uploaded_file):
    """Proses file yang diunggah dan kembalikan DataFrame."""
    df = pd.read_excel(uploaded_file)
    columns_to_keep = ["Date", "Flight", "Dep", "Arr", "Reg", "Uplift_in_Lts", "Invoice"]
    df = df[columns_to_keep]
    df.columns = ["Date", "Flight", "Dep", "Arr", "Reg", "Uplift_in_Lts", "Invoice"]
    return df


def save_data_to_database(df, request):
    """Simpan data dari DataFrame ke database."""
    successful_invoices = []
    failed_invoices = []

    for index, row in df.iterrows():
        vendor = request.POST.get("vendor")
        fuel_vendor = FuelVendor(
            Date=row["Date"],
            Flight=row["Flight"],
            Dep=row["Dep"],
            Arr=row["Arr"],
            Reg=row["Reg"],
            Uplift_in_Lts=float(row["Uplift_in_Lts"]),
            Invoice=row["Invoice"],
            Vendor=vendor,
        )
        if FuelVendor.objects.filter(Invoice=row["Invoice"]).exists():
            failed_invoices.append(row["Invoice"])
        else:
            fuel_vendor.save()
            successful_invoices.append(row["Invoice"])

    return successful_invoices, failed_invoices



def index(request):
    if request.method == "POST":
        if 'file' in request.FILES and request.FILES['file'].name.endswith('.xlsx') and request.POST.get("date_of_data") is not None:
            uploaded_file = request.FILES["file"]
            df = process_uploaded_file(uploaded_file)
            successful_invoices, failed_invoices = save_data_to_database(df, request)
            
            # Mendapatkan tanggal data dari form
            date_of_data = request.POST.get("date_of_data")

            # Proses lainnya...
            if (date_of_data is not None):  
                formatted_date = datetime.strptime(date_of_data, "%Y-%m-%d").strftime("%d/%m/%Y")
                fuel_occ = get_data_from_sheet_by_date(
                    "Fuel_Uplift_by_Departure_Station", "test_occ", formatted_date)
                
                print(fuel_occ)

            if fuel_occ is not None and fuel_vendor is not None:
                for i in range(len(fuel_occ)):
                    fuel_occ[i]["Uplift_in_Lts"] = float(fuel_occ[i]["Uplift_in_Lts"])

                for i in range(len(fuel_vendor)):
                    fuel_vendor[i].Uplift_in_Lts = float(fuel_vendor[i].Uplift_in_Lts)

            if fuel_occ is not None and fuel_vendor is not None:
                len_fuel_occ = len(fuel_occ)
                len_fuel_vendor = len(fuel_vendor)

                if len_fuel_occ == len_fuel_vendor:
                    print("Data sama")
                    for i in range(len_fuel_occ):
                        if fuel_occ[i]["Invoice"] == fuel_vendor[i].Invoice:
                            if fuel_occ[i]["Uplift_in_Lts"] != fuel_vendor[i].Uplift_in_Lts:
                                missing_data_vendor.append(fuel_vendor[i])
                                missing_data_occ.append(fuel_occ[i])

                elif len_fuel_occ > len_fuel_vendor:
                    print("Data fuel_occ lebih banyak")
                    for i in range(len_fuel_vendor):
                        if fuel_occ[i]["Invoice"] == fuel_vendor[i].Invoice:
                            if fuel_occ[i]["Uplift_in_Lts"] != fuel_vendor[i].Uplift_in_Lts:
                                missing_data_vendor.append(fuel_vendor[i])
                                missing_data_occ.append(fuel_occ[i])

                        if fuel_vendor[i].Invoice not in [
                            fuel_occ[j]["Invoice"] for j in range(len_fuel_occ)
                        ]:
                            missing_invoice_vendor.append(fuel_vendor[i])

                elif len_fuel_occ < len_fuel_vendor:
                    fuel_occ_invoices = set(item["Invoice"] for item in fuel_occ)
                    for vendor_item in fuel_vendor:
                        if vendor_item.Invoice in fuel_occ_invoices:
                            occ_item = next(
                                item
                                for item in fuel_occ
                                if item["Invoice"] == vendor_item.Invoice
                            )
                            if occ_item["Uplift_in_Lts"] != vendor_item.Uplift_in_Lts:
                                missing_data_vendor.append(vendor_item)
                                missing_data_occ.append(occ_item)
                        else:
                            missing_invoice_vendor.append(vendor_item)

            if missing_data_vendor and missing_data_occ:
                for i in range(len(missing_data_vendor)):
                    print(missing_data_vendor[i])

                    date_occ_formatted = datetime.strptime(
                        missing_data_occ[i]["Date"], "%d/%m/%Y"
                    ).strftime("%Y-%m-%d")

                    date_ven_formatted = (
                        missing_data_vendor[i].Date.strftime("%Y-%m-%d")
                        if isinstance(missing_data_vendor[i].Date, datetime)
                        else missing_data_vendor[i].Date
                    )

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
                    )
                    missing_data_obj.save()

            if missing_invoice_vendor:
                for i in range(len(missing_invoice_vendor)):
                    print(missing_invoice_vendor[i].Invoice)

                    date_formated = (
                        missing_invoice_vendor[i].Date.strftime("%Y-%m-%d")
                        if isinstance(missing_invoice_vendor[i].Date, datetime)
                        else missing_invoice_vendor[i].Date
                    )

                    missing_invoice_obj = MissingInvoice(
                        date=date_formated,
                        flight=missing_invoice_vendor[i].Flight,
                        departure=missing_invoice_vendor[i].Dep,
                        arrival=missing_invoice_vendor[i].Arr,
                        registration=missing_invoice_vendor[i].Reg,
                        uplift_in_lts=missing_invoice_vendor[i].Uplift_in_Lts,
                        invoice_no=missing_invoice_vendor[i].Invoice,
                    )
                    missing_invoice_obj.save()

            if successful_invoices:
                successful_invoices_str = [str(invoice) for invoice in successful_invoices]
                messages.success(
                    request, f"Data dengan invoice {', '.join(successful_invoices_str)} berhasil ditambahkan ke database.",
                )
                successful_invoices = []

            if failed_invoices:
                failed_invoices_str = [str(invoice) for invoice in failed_invoices]
                messages.error(
                    request,
                    f"Data dengan invoice {', '.join(failed_invoices_str)} sudah ada di database.",
                )
                failed_invoices = []

            return redirect(reverse("VendorApp:index"))

    reconsiliasi = Reconsiliasi.objects.all()
    context = {"page_title": "Home", "Reconsiliasi": reconsiliasi}
    return render(request, "index.html", context)
