from django import forms 
from user_app.models import *

class UserRegistrationform(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username','email','phone','password']


class VechicleRegistrationForm(forms.ModelForm):
    
    class Meta:

        model = Vehicle

        fields = ['brand','model','connector_type','vin','registration_num']

class EVservicerq(forms.ModelForm):
    class Meta:
        model = EVService
        fields = ['category','description']
        widgets = {
            'description': forms.Textarea(attrs={'class':'form-control', 'rows':3, 'placeholder':'Enter description'}),
            'price': forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Enter price'}),
            'category': forms.Select(attrs={'class':'form-select'}),
            'status': forms.Select(attrs={'class':'form-select'}),
         }


