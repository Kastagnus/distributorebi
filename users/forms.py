from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser

class UserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'ltd_name', 'identification_number', 'phone_number', 'brand_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom attributes for styling
        self.fields['email'].widget.attrs.update({'class': 'form-control', 'required': True})
        self.fields['full_name'].widget.attrs.update({'class': 'form-control',})
        self.fields['ltd_name'].widget.attrs.update({'class': 'form-control', 'required': True})
        self.fields['identification_number'].widget.attrs.update({'class': 'form-control', 'required': True})
        self.fields['phone_number'].widget.attrs.update({'class': 'form-control', 'required': True})
        self.fields['brand_name'].widget.attrs.update({'class': 'form-control',})
        self.fields['password1'].widget.attrs.update({'class': 'form-control',})
        self.fields['password2'].widget.attrs.update({'class': 'form-control',})

class MyLoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'password')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control',})
        self.fields['password'].widget.attrs.update({'class': 'form-control',})
