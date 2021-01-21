from datetime import datetime
import pytz
from decimal import Decimal
import numpy as np

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Avg, Value, CharField, ExpressionWrapper, F, Sum, FloatField, DecimalField, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, View, TemplateView
from django.http import JsonResponse, Http404

from home.decorators import client_required
from ..forms import PortfolioCreationForm
from home.models import User, Client
from ..models import Portfolio, StockTransactRecord, Stock


class GuestOverview(TemplateView):
    '''Display Table product information to guest.'''
    template_name = 'table/guests/guest_overview.html'

    def get_context_data(self, **kwargs):
        context = super(GuestOverview, self).get_context_data(**kwargs)
        context['market_data'] = Stock.get_stocks_data(dates=['2000-01-01', '2020-01-01'], tickers=['^DJI', '^GSPC', '^IXIC', 'IBM'])
        context['marketing_message'] = "Make an Account Today!"
        return context