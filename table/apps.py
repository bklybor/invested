from django.apps import AppConfig


class TableConfig(AppConfig):
    name = 'table'

    def ready(self):

        from table.models import StockTransactRecord, site_settings, stock_management_settings
        from home.models import Company
        from settings.models import SiteSettings, StockManagementSettings
        from .decision_tables.decision_tables import StockTransactRecordDecisionTable

        from utils.decision_table import decision_table

        site_settings = SiteSettings.objects.all()[0]
        stock_management_settings = StockManagementSettings.objects.all()[0]
        company = Company.objects.all()[0]
        company_master_portfolio = company.user.portfolios.all()[0]

        StockTransactRecordDecisionTable.company_master_portfolio = company_master_portfolio
        StockTransactRecordDecisionTable.stock_management_settings = stock_management_settings
        StockTransactRecordDecisionTable.model = StockTransactRecord

        StockTransactRecord.decision_table = StockTransactRecordDecisionTable()
        StockTransactRecord.decision_table.setup_decision_table()
        