
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
            'county',
            'town',
            'area',
            'rental_price',
            'rental_period',
            'available'
        ]

        labels = {
            'rental_price': 'Rental Price (KSh)',
            'rental_period': 'Rental Period',
            'county': 'County',
            'town': 'Town',
            'area': 'Specific Area / Nearby Landmark'
        }

        widgets = {
            'county': forms.Select(attrs={
                'class': 'form-control'
            }),

            'town': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter town, e.g. Naivasha'
            }),

            'area': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter area or nearby landmark (optional)'
            }),

            'rental_period': forms.Select(attrs={
                'class': 'form-control'
            }),
        }


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
