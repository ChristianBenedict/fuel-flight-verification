from django.db import models

class FuelOcc(models.Model):
    Date = models.DateField()
    Flight = models.CharField(max_length=50)
    Dep = models.CharField(max_length=100)  
    Arr = models.CharField(max_length=100) 
    Reg = models.CharField(max_length=20)
    Uplift_in_Lts = models.FloatField()
    Uplift_in_Usg = models.FloatField()
    Invoice = models.CharField(max_length=100)
    
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
    
    Vendor = models.CharField(max_length=100, null=True, blank=True, choices=VENDOR_CHOICES) 

    def __str__(self):
        return f"{self.Date} - {self.Flight} - {self.Reg}"

