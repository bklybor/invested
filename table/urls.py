from django.urls import include, path
from .views import table, broker, client, guest

app_name = 'table'

urlpatterns = [
    path('', table.home, name= 'home'),
    
    path('client/', include(([
        path('overview/', client.ClientOverview.as_view(), name= 'client_home_view'),
        path('portfolios/<portfolio_name>', client.ClientPortfolioView.as_view(), name='client_portfolio_view')
    ], 'table'), namespace= 'client')),

    path('broker/', include(([
        path('', broker.BrokerHomeView.as_view(), name= 'broker_home_view'),
    ], 'broker'), namespace= 'broker')),

    path('guest/', include(([
        path('', guest.GuestOverview.as_view(), name= 'guest_home_view'),
    ], 'guest'), namespace= 'guest')),

]