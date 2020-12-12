from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.forms.utils import ValidationError

from home.models import User, Client, Broker
from .models import Portfolio, StockTransactRecord


class PortfolioCreationForm(forms.ModelForm):
    """Form for creating a new portfolio"""
    class Meta:
        model = Portfolio
        fields = ['name', 'cash']
        labels = {
            'name': 'Portfolio Name',
            'cash': 'Initial Investment'
        }
        help_texts = {
            'name': 'The name for your new portfolio.',
            'cash': 'Your initial investment'
        }

    def __init__(self, *args, **kwargs):
        super(PortfolioForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        data = self.cleaned_data['name']
        if not isinstance(data, str):
            raise ValidationError('Name is not a string.')
        return data
        
    def clean_cash(self):
        data = self.cleaned_data['cash']
        try:
            Decimal(data)
        except:
            raise ValidationError('Could not parse decimal number.')
        return data