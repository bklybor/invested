from django.contrib import admin

from .models import SiteSettings, StockManagementSettings, CashManagementSettings
from home.models import Company

class SingletonModelAdmin(admin.ModelAdmin):
    """
    
    """
    actions= None

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    
@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonModelAdmin):
    pass

@admin.register(StockManagementSettings)
class StockManagementSettingsAdmin(SingletonModelAdmin):
    pass

@admin.register(Company)
class CompanyAdmin(SingletonModelAdmin):
    pass

@admin.register(CashManagementSettings)
class CashManagementSettingsAdmin(SingletonModelAdmin):
    pass