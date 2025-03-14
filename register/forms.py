# register/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from decimal import Decimal
from payapp.utils import convert_currency

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    currency = forms.ChoiceField(choices=[('GBP', 'GB Pounds'), ('USD', 'US Dollars'), ('EUR', 'Euros')], required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'currency', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.currency = self.cleaned_data['currency']
        # Use the RESTful service for conversion
        if user.currency != 'GBP':
            converted_balance, _ = convert_currency(Decimal('750'), 'GBP', user.currency)
            user.balance = converted_balance
        else:
            user.balance = Decimal('750')
        if commit:
            user.save()
        return user