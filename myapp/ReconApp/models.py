from django.db import models
from django.forms import ValidationError


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
    date = models.DateField(blank=True, null=True)
    flight = models.CharField(max_length=100, default='', blank=True, null=True)
    departure = models.CharField(max_length=100, default='', blank=True, null=True)
    arrival = models.CharField(max_length=100, default='', blank=True, null=True)
    registration = models.CharField(max_length=100, default='', blank=True, null=True)
    uplift_in_lts = models.FloatField(default=0, blank=True, null=True)
    invoice_no = models.CharField(max_length=100, default='', blank=True, null=True)
    fuel_agent = models.CharField(max_length=100, default='', blank=True, null=True)
    
    
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
    date = models.DateField(blank=True, null=True)
    flight = models.CharField(max_length=100, default='', blank=True, null=True)
    departure = models.CharField(max_length=100, default='', blank=True, null=True)
    arrival = models.CharField(max_length=100, default='', blank=True, null=True)
    registration = models.CharField(max_length=100, default='', blank=True, null=True)
    uplift_in_lts = models.FloatField(default=0, blank=True, null=True)
    invoice_no = models.CharField(max_length=100, default='', blank=True, null=True)
    fuel_agent = models.CharField(max_length=100, default='', blank=True, null=True)
    
    def __str__(self):
        return f"{self.date} - {self.flight} - {self.registration}"
    
    def save(self, *args, **kwargs):
        try:
            super().save(*args, **kwargs)
        except ValidationError as e:
            print(f"Error saving MissingInvoiceInOcc: {e}")
            print(f"Invalid values: uplift_in_lts={self.uplift_in_lts}")