from django.db import models

class Homepage_stock_list(models.Model):
    tradingsymbol = models.CharField(max_length=255)
    symboltoken = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.tradingsymbol} ({self.symboltoken})"