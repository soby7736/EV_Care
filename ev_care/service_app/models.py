from django.db import models

# Create your models here.


class Service_Centre(models.Model):
    name = models.CharField(max_length=100)
    phone= models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    # password = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    longitude = models.DecimalField(decimal_places=10,max_digits=20,null=True,blank=True)
    latitude = models.DecimalField(decimal_places=10,max_digits=20,null=True,blank=True)
    image = models.ImageField(upload_to='service_center_photos/', null=True, blank=True)
    working_hours = models.CharField(max_length=55,default="")
    utype = models.CharField(max_length=20,default='service_centre')
    status = models.CharField(max_length=20,default='pending')


class Products(models.Model):
    service_centre = models.ForeignKey(Service_Centre,on_delete=models.CASCADE,null=True,blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2,max_digits=10,null=True,blank=True)
    quantity = models.CharField(max_length=50,)
    image = models.FileField(upload_to="product_images",null=True,blank=True)
