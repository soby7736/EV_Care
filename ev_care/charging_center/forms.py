from django import forms
from charging_center.models import *


class ChargingRegister(forms.ModelForm):
    class Meta:
        model = ChargingStations
        fields = ['name','image','location','address','latitude','longitude','working_hours','connectors','rate_per_slot','capacity']


class ChargingsloteCreation(forms.ModelForm):
    class Meta:
        model = ChargingSlot
        fields = ['start_time','end_time']