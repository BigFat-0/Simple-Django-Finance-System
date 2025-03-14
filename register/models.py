from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    currency = models.CharField(max_length=3, choices=[('GBP', 'GB Pounds'), ('USD', 'US Dollars'), ('EUR', 'Euros')], default='GBP')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=750.00)


    def __str__(self):
        return self.username