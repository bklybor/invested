import pandas as pd
from datetime import datetime
import pytz
from decimal import Decimal
import pandas as pd
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

pd.set_option('display.max_columns', None)

'''@method_decorator([login_required, client_required], name= 'dispatch')
class ClientHomeView(View):
    model = Client
    context_object_name = 'client_info'
    template_name = 'table/clients/client_view.html'
    queyset = Client.objects.all()

    def get_queryset(self):
        return Portfolio.objects.filter(owner= self.client_id)'''


@method_decorator([login_required, client_required], name= 'dispatch')
class ClientOverview(TemplateView):
    '''Passes general overview content to the Client's Talbe Overview page.'''
    template_name = 'table/clients/client_overview.html'

    def get_portfolio_queryset(self):
        return self.request.user.client.get_portfolios_values()

    def get_context_data(self, **kwargs):
        context = super(ClientOverview, self).get_context_data(**kwargs)
        context['market_data'] = Stock.get_stocks_data(dates=['2000-01-01', '2020-01-01'], tickers=['^DJI', '^GSPC', '^IXIC', 'IBM'])
        return context


@method_decorator([login_required, client_required], name= 'dispatch')
class ClientPortfolioView(TemplateView):
    '''Detailed view of a given portfolio.'''
    template_name = 'table/clients/client_portfolio_view.html'

    def get_portfolio(self, test_name):
        names = list(self.request.user.portfolios.all().values_list('name'))
        names_list = [item[0] for item in names]
        portfolio = None
        if test_name in names_list:
            portfolio = self.request.user.portfolios.get(name= test_name)
        else:
            raise Http404

        return portfolio

    def get_context_data(self, **kwargs):
        context = super(ClientPortfolioView, self).get_context_data(**kwargs)
        context['portfolio'] = self.get_portfolio(context['portfolio_name'])
        
        return context

