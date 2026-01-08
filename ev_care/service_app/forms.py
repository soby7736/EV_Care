from django import forms 
from service_app.models import *

class ServiceCenterForm(forms.ModelForm):
    class Meta:
        model = Service_Centre
        exclude =('utype','status')


class CreateProduct(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['name', 'description', 'price', 'quantity', 'image']