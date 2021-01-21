from django.test import TestCase

from table.models import StockTransactRecord, Portfolio, StockInventory
from home.models import Company, User, Client
from settings import context_processors

class ClientStockTransactionTest(TestCase):

    @classmethod
    def setUpTestData(cls):

        cls.COMPANY_CASH = 100000000 # start company with 100 million USD
        cls.CLIENT_CASH = 100000 # start client with 100 thousand USD

        context_processors.site_settings(None)
        context_processors.stock_management_settings(None)
        company_user = User.objects.create(is_company= True, username= 'TheCompany', email= 'thecompany@thecompany.com', password= '123123123')
        Company.objects.create(user= company_user)
        Portfolio.objects.create(owner= Company.objects.all()[0].user)#, name= 'company_master_portfolio', cash= 100 000 000, )
        context_processors.company_settings(None)

        cls.company_master_portfolio = Company.objects.all()[0].user.portfolios.all()[0]
        cls.company_master_portfolio.name= 'company_master_portfolio'
        cls.company_master_portfolio.cash = cls.COMPANY_CASH
        cls.company_master_portfolio.save()
        # start company master portfolio with 1000 shares of IBM
        sti = StockInventory(portfolio= cls.company_master_portfolio, ticker= 'IBM', exchange_abbr= 'NYSE', quantity= 10000)
        sti.save()

        StockTransactRecord.decision_table.company_master_portfolio= cls.company_master_portfolio
        #StockTransactRecord.decision_table.stock_management_settings = cls.stock_management_settings

    def test_internal_stock_transaction(self):
        user = User(is_client= True, password= '12345', username= 'client1', email= 'client1@gmail.com')
        user.save()
        client = Client.objects.create(user= user)
        # start client portfolio with 100000 in cash
        client_portfolio = Portfolio.objects.create(owner= client.user, cash= self.__class__.CLIENT_CASH, name= 'first')
        
        # buy order for 100 shares of IBM at 100 USD per share
        stock_transaction = StockTransactRecord(portfolio= client_portfolio, ticker= 'IBM', exchange_abbr= 'NYSE', order_type= 'buy', order_class= 'undetermined', price= 100, quantity= 100)
        stock_transaction.save()

        self.assertEqual(client_portfolio.stockinventory.get(ticker= 'IBM').quantity, 100)
        print('(client portfolio successfully acquired 100 shares of IBM.)')
        self.assertEqual(client_portfolio.cash, 90000)
        print('(client portfolio cash reduced from $100,000 to $90,000)')
        self.assertEqual(client_portfolio.stocktransactions.last().ticker, 'IBM')
        print('(last stock transaction for client portfolio is for IBM)')
        self.assertEqual(self.__class__.company_master_portfolio.stockinventory.get(ticker= 'IBM').quantity, 9900)
        print('(100 shares of IBM subtracted from company_master_portfolio)')
        
