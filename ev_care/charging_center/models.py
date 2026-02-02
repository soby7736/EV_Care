from django.db import models
from datetime import datetime, timedelta

# Create your models here.

class ChargingStations(models.Model):
    name = models.CharField(max_length=200)
    image = models.ImageField(upload_to='ev_station/')
    address = models.TextField()
    location = models.URLField()
    latitude = models.DecimalField(max_digits=9,decimal_places=6,help_text="Latitude of the station")
    longitude = models.DecimalField(max_digits=9,decimal_places=6,help_text="Longitude of the station")
    working_hours = models.CharField(max_length=50)
    CONNECTOR_CHOICES = [
        ('type1', 'Type 1'),
        ('type2', 'Type 2'),
        ('ccs2', 'CCS2'),
        ('gbt', 'GB/T'),
        ('chademo', 'CHAdeMO'),
    ]
    connectors = models.CharField(
        max_length=100,
        choices=CONNECTOR_CHOICES
    )

    rate_per_slot = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    capacity = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ChargingSlot(models.Model):
    station = models.ForeignKey(ChargingStations,on_delete=models.CASCADE,related_name='slots')
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

