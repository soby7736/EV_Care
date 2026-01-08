from django.db import models
from service_app.models import *

from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):

    phone = models.CharField(max_length=15)


#  Vechichle Registration
class Vehicle(models.Model):
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE,null=True,blank=True)
    brand = models.CharField(max_length=100,null=True,blank=True)
    model = models.CharField(max_length=100,null=True,blank=True)
    connector_type = models.CharField(max_length=100,choices=[('type1', 'Type 1'),
        ('type2', 'Type 2'),
        ('ccs2', 'CCS2'),
        ('gbt', 'GB/T'),
        ('chademo', 'CHAdeMO'),])
    vin = models.CharField(max_length=30,null=True,blank=True)
    registration_num = models.CharField(max_length=100,null=True)

class EVService(models.Model):

    SERVICE_CATEGORY_CHOICES = [
        ('software', 'Software Update'),
        ('charging', 'Charging Service'),
        ('battery', 'Battery Service'),
        ('water', 'Water Wash'),
        ('mechanical', 'Mechanical Service'),
        ('electrical', 'Electrical Service'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('completed', 'Completed'),
    ]
    category = models.CharField(max_length=20,choices=SERVICE_CATEGORY_CHOICES)
    service_centre = models.ForeignKey(Service_Centre,on_delete=models.CASCADE,related_name='ev_services')
    user = models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES,default='pending')
    price = models.DecimalField(max_digits=8,decimal_places=2,null=True,blank=True)
    payment = models.TextField(choices=[('pending','pending'),
                                        ('completed','completed')],default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class ServicePayment(models.Model):
    service = models.OneToOneField(EVService,on_delete=models.CASCADE,related_name="service_payment")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('online', 'Online'),
            ('cash', 'Cash'),
        ]
    )

    # Razorpay fields (only for online payment)
    razorpay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razorpay_signature = models.TextField(null=True, blank=True)

    is_paid = models.BooleanField(default=False)
    paid_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)



class ProductOrder(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    service_centre = models.ForeignKey(Service_Centre, on_delete=models.CASCADE, null=True, blank=True)

    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'), 
        ('received', 'Received'),
    )

    order_status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending'
    )
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)

    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.price = self.product.price
        self.total_amount = self.price * self.quantity
        super().save(*args, **kwargs)


  


