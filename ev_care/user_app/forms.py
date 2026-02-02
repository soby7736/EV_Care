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
            'category': forms.Select(attrs={'class':'form-select'}),
         }
        

# class SlotBookingForm(forms.ModelForm):
#     class Meta:
#         model = SlotBooking
#         fields = ["start_time", "end_time"]
#         widgets = {
#             "start_time": forms.TimeInput(attrs={"type": "time"}),
#             "end_time": forms.TimeInput(attrs={"type": "time"}),
#         }


