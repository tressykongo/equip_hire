
from django import forms
from .models import Equipment, RentalRequest


class EquipmentForm(forms.ModelForm):

    class Meta:
        model = Equipment
        fields = [
            'name',
            'description',
            'image',
            'category',
            'rental_price',
            'available'
        ]


class RentalRequestForm(forms.ModelForm):

    class Meta:
        model = RentalRequest
        fields = ['message']

        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Tell the equipment owner about your hiring needs...'
            })
        }

        labels = {
            'message': 'Message to Equipment Owner'
        }
