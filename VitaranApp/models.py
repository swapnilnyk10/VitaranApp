from email.policy import default
from tokenize import Name
from unicodedata import decimal
from unittest.util import _MAX_LENGTH
from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Profile(models.Model):
    def __str__(self):
        return f'{self.Name} {self.Employee_ID}'
    # user = models.OneToOneField(User,on_delete=models.CASCADE)
    Name = models.CharField(max_length=100)
    Employee_ID = models.CharField(max_length=15)
    Email = models.EmailField()
    quarter_no = models.CharField(max_length=15)
    meter_no = models.IntegerField()
    OTP = models.CharField(max_length=4, default = 0)

class Bill(models.Model):
    def __str__(self):
        return f' {self.Name} {self.month} {self.year}'
    quarter_no = models.CharField(max_length=15, default = "NA")
    Name = models.CharField(max_length=100, default="NA")
    meter_no = models.IntegerField(default = 0)
    sanction_load = models.IntegerField(default = 0)
    Employee_ID = models.CharField(max_length=15, default="0")
    previous_units = models.IntegerField()
    KVA_charge = models.DecimalField(default = 0, decimal_places = 2, max_digits = 10)
    current_units = models.IntegerField()
    net_billed_unit = models.IntegerField(default = 0)
    month = models.CharField(max_length=12)
    year = models.IntegerField(default = 0)
    rateP1 = models.DecimalField(default = 0, decimal_places = 2, max_digits = 10)
    unitP1 = models.IntegerField(default = 0)
    rateP2 = models.DecimalField(default = 0, decimal_places = 2, max_digits = 10)
    unitP2 = models.IntegerField(default = 0)
    rateP3 = models.DecimalField(default = 0, decimal_places = 2, max_digits = 10)
    unitP3 = models.IntegerField(default = 0)
    rateP4 = models.DecimalField(default = 0, decimal_places = 2, max_digits = 10)
    unitP4 = models.IntegerField(default = 0)
    rateP5 = models.DecimalField(default = 0, decimal_places = 2, max_digits = 10)
    unitP5 = models.IntegerField(default = 0)
    rateP6 = models.DecimalField(default = 0, decimal_places = 2, max_digits = 10)
    payable_amount = models.DecimalField(default=0, decimal_places = 2, max_digits = 10)