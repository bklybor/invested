from .models import SiteSettings, StockManagementSettings, CashManagementSettings
from home.models import Company

def site_settings(request):
    return {'site_settings': SiteSettings.load()}

def stock_management_settings(request):
    return {'stock_management_settings': StockManagementSettings.load()}

def company_settings(request):
    return {'company_settings': Company.load()}

def cash_management_settings(request):
    return {'cash_management_settings': CashManagementSettings.load()}