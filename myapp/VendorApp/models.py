from django.db import models

class FuelVendor(models.Model):
    Date = models.DateField()
    Flight = models.CharField(max_length=50)
    Dep = models.CharField(max_length=100)  
    Arr = models.CharField(max_length=100) 
    Reg = models.CharField(max_length=20)
    Uplift_in_Lts = models.FloatField()
    Invoice = models.CharField(max_length=100)
    Vendor= models.CharField(max_length=150)
    
    

    def __str__(self):
        return f"{self.Date} - {self.Flight} - {self.Reg} - {self.Invoice}- {self.Vendor}"

