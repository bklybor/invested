from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count, Avg
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView, View

from home.decorators import client_required
from ..forms import PortfolioCreationForm
from home.models import User, Client
from ..models import Portfolio, StockTransactRecord

class BrokerHomeView(ListView):
    model = Portfolio
    ordering = ('open_date',)
    context_object_name = 'client_home_view'
    template_name = 'table/home.html'

    def get_queryset(self):
        queryset = self.request.user.portfolios.all()
        
        temp = queryset[0].name
        #Portfolio.objects.filter(owner= self.request.user).order_by('open_date')

        return queryset