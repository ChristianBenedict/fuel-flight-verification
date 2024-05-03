from django.db import models
from django.forms import ValidationError

class Reconsiliasi(models.Model):
    date_occ = models.DateField()
    flight_occ = models.CharField(max_length=50)
    departure_occ = models.CharField(max_length=100)  
    arrival_occ = models.CharField(max_length=100) 
    registration_occ = models.CharField(max_length=20)
    uplift_in_lts_occ = models.FloatField()
    
    date_ven = models.DateField()
    flight_ven = models.CharField(max_length=50)
    departure_ven = models.CharField(max_length=100)  
    arrival_ven = models.CharField(max_length=100) 
    registration_ven = models.CharField(max_length=20)
    uplift_in_lts_ven = models.FloatField()
    
    invoice_no= models.CharField(max_length=100)

    VENDOR_CHOICES = [
        ('pertamina', 'Pertamina'),
        ('petronas_dagangan', 'Petronas Dagangan'),
        ('pttor', 'PTTOR'),
        ('bafs', 'BAFS'),
        ('petronas_dagangan_berhad', 'Petronas Dagangan Berhad'),
        ('shell', 'Shell'),
        ('petron', 'Petron'),
        ('airbp', 'AIRBP'),
        ('ptt_public_co_ltd', 'PTT Public Co. Ltd'),
        ('singapore_petroleum_company_limited', 'Singapore Petroleum Company Limited'),
        ('shell_malaysia_trading', 'Shell Malaysia Trading'),
    ]
    vendor = models.CharField(max_length=100, null=True, blank=True, choices=VENDOR_CHOICES) 

    def __str__(self):
        return f"{self.date_occ} - {self.flight_occ} - {self.registration_occ}"
    
    
    
# ini adalah model untuk missing invoice khusus untuk vendor
class MissingInvoice(models.Model):
    date = models.DateField()
    flight = models.CharField(max_length=50)
    departure = models.CharField(max_length=100)  
    arrival = models.CharField(max_length=100) 
    registration = models.CharField(max_length=20)
    uplift_in_lts = models.FloatField()
    invoice_no= models.CharField(max_length=100)
    Vendor= models.CharField(max_length=150)
    
    def __str__(self):
        return f"{self.date} - {self.flight} - {self.registration}"
    
    

# ini adalah model untuk missing invoice khusus untuk occ
class MissingInvoiceOcc (models.Model):
    date = models.DateField()
    flight = models.CharField(max_length=50)
    departure = models.CharField(max_length=100)  
    arrival = models.CharField(max_length=100) 
    registration = models.CharField(max_length=20)
    uplift_in_lts = models.FloatField()
    invoice_no= models.CharField(max_length=100)
    vendor = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.date} - {self.flight} - {self.registration}"
    
    


class Result (models.Model):
    time_of_event= models.DateTimeField(auto_now_add=True)
    data_start_date= models.DateField()
    data_end_date= models.DateField()
    total_uplift_in_lts_occ= models.FloatField()
    total_uplift_in_lts_ven= models.FloatField()
    total_selisih= models.FloatField()
    fuel_agent= models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.id} - {self.time_of_event}"
    
    
    



class DetailResult(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='detail_results')
    date_occ = models.DateField()
    flight_occ = models.CharField(max_length=100)
    departure_occ = models.CharField(max_length=100)
    arrival_occ = models.CharField(max_length=100)
    registration_occ = models.CharField(max_length=100)
    uplift_in_lts_occ = models.FloatField(default=0)
    date_ven = models.DateField()
    flight_ven = models.CharField(max_length=100)
    departure_ven = models.CharField(max_length=100)
    arrival_ven = models.CharField(max_length=100)
    registration_ven = models.CharField(max_length=100)
    uplift_in_lts_ven = models.FloatField(default=0)
    invoice_no = models.CharField(max_length=100)
    fuel_agent = models.CharField(max_length=100)
    selisih = models.FloatField(default=0) 
    
    def __str__(self):
        return f"{self.date_occ} - {self.flight_occ} - {self.registration_occ}"
    
    def save(self, *args, **kwargs):
        # Hitung selisih
        self.selisih = self.uplift_in_lts_occ - self.uplift_in_lts_ven

        try:
            # Coba menyimpan nilai
            super().save(*args, **kwargs)
        except ValidationError as e:
            # Jika terjadi kesalahan validasi, cetak pesan kesalahan dan nilai yang menyebabkannya
            print(f"Error saving DetailResult: {e}")
            print(f"Invalid values: uplift_in_lts_occ={self.uplift_in_lts_occ}, uplift_in_lts_ven={self.uplift_in_lts_ven}")
            
            

class MissingInvoiceInVendor(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='missing_invoices_in_vendor')
    date = models.DateField()
    flight = models.CharField(max_length=100)
    departure = models.CharField(max_length=100)
    arrival = models.CharField(max_length=100)
    registration = models.CharField(max_length=100)
    uplift_in_lts = models.FloatField(default=0)
    invoice_no = models.CharField(max_length=100)
    fuel_agent = models.CharField(max_length=100)
    
    
    def __str__(self):
        return f"{self.date} - {self.flight} - {self.registration}"
    
    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except ValidationError as e:
            print(f"Error saving MissingInvoiceInVendor: {e}")
            print(f"Invalid values: uplift_in_lts={self.uplift_in_lts}")
            

class MissingInvoiceInOcc(models.Model):
    result = models.ForeignKey(Result, on_delete=models.CASCADE, related_name='missing_invoices_in_occ')
    date = models.DateField()
    flight = models.CharField(max_length=100)
    departure = models.CharField(max_length=100)
    arrival = models.CharField(max_length=100)
    registration = models.CharField(max_length=100)
    uplift_in_lts = models.FloatField(default=0)
    invoice_no = models.CharField(max_length=100)
    fuel_agent = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.date} - {self.flight} - {self.registration}"
    
    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except ValidationError as e:
            print(f"Error saving MissingInvoiceInOcc: {e}")
            print(f"Invalid values: uplift_in_lts={self.uplift_in_lts}")