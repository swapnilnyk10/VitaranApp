from email.policy import default
from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Profile(models.Model):
    def __str__(self):
        return f'{self.first_name} {self.last_name} {self.Employee_ID}'
    # user = models.OneToOneField(User,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    # user.password1 = None
    # user.password2 = None
    Employee_ID = models.CharField(max_length=15)
    Phone = models.IntegerField()
    Email = models.EmailField()
    quarter_no = models.CharField(max_length=6)
    meter_no = models.IntegerField()
    OTP = models.CharField(max_length=4, default = 0)

class Bill(models.Model):
    def __str__(self):
        return f' {self.Employee_ID} {self.month} {self.year}'
    Employee_ID = models.IntegerField()
    month = models.CharField(max_length=12)
    year = models.IntegerField()
    tariff= models.IntegerField()
    previous_units = models.IntegerField()
    current_units = models.IntegerField()
    net_billed_amount = models.IntegerField(default=0)
    payable_amount = models.IntegerField(default=0)
    