from django import forms
# from django.utils import timezone
from bookings.models import Booking
from django.contrib.auth import get_user_model

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['show_date']
        widgets = {
            'show_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Select show date',
            }),
        }
        labels = {
            'show_date': 'Select Show Date',
        }

User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'city']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your full name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@gmail.com'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
        }
        labels = {
            'name': 'Name',
            'email': 'Email',
            'city': 'City',
        }
