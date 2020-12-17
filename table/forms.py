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

class StockOrderForm(forms.ModelForm):
    """Form for submitting a stock order."""
    class Meta:
        model = StockTransactRecord
        fields = ['exchange_abbr', 'ticker', 'order_type', 'order_placement_datetime','order_execution_datetime', 'price', 'quantity']
        labels = {
            'exchange_abbr': 'Exchange',
            'ticker': 'Ticker',
            'order_type': 'Order Type',
            'order_placement_date': 'Order Placement Date',
            'order_execution_date': 'Order Execution Date',
            'price': 'Price',
            'quantity': 'Quantity'
        }
        help_texts = {

        }

        def __init__(self, *args, **kwargs):
            super(PortfolioForm, self).__init__(*args, **kwargs)

        def clean_(self):
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