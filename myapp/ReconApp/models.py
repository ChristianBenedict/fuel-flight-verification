from django.db import models

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
    
    