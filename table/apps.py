from django.apps import AppConfig


class TableConfig(AppConfig):
    name = 'table'

    def ready(self):

        from table.models import StockTransactRecord, CashTransactionRecord, site_settings
        from home.models import Company
        from settings.models import SiteSettings, StockManagementSettings , CashManagementSettings
        from .decision_tables.decision_tables import StockTransactRecordDecisionTable, CashTransactionRecordDecisionTable

        from utils.decision_table import decision_table

        site_settings, created = SiteSettings.objects.get_or_create()
        stock_management_settings, created = StockManagementSettings.objects.get_or_create()
        cash_management_settings, created = CashManagementSettings.objects.get_or_create()
        company, created = Company.objects.get_or_create()
        company.user.is_company = True
        company_master_portfolio, created = company.user.portfolios.get_or_create()

        StockTransactRecordDecisionTable.company_master_portfolio = company_master_portfolio
        StockTransactRecordDecisionTable.stock_management_settings = stock_management_settings
        StockTransactRecordDecisionTable.site_settings = site_settings
        StockTransactRecordDecisionTable.model = StockTransactRecord
        StockTransactRecord.decision_table = StockTransactRecordDecisionTable()
        StockTransactRecord.decision_table.setup_decision_table()

        CashTransactionRecordDecisionTable.site_settings = site_settings
        CashTransactionRecordDecisionTable.cash_management_settings = cash_management_settings
        CashTransactionRecord.decision_table = CashTransactionRecordDecisionTable()
        CashTransactionRecord.decision_table.setup_decision_table()
        
        