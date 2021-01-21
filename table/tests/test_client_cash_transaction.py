from django.test import TestCase

from table.models import CashTransactionRecord, Portfolio
from home.models import Company, User, Client
from settings import context_processors

class ClientCashTransactionTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        print(CashTransactionRecord.decision_table)
        cls.CLIENT_START_CASH = 10000 # start client with 10 thousand USD

        context_processors.site_settings(None)
        context_processors.cash_management_settings(None)
        company_user = User.objects.create(is_company= True, username= 'TheCompany', email= 'thecompany@thecompany.com', password= '123123123')
        Company.objects.create(user= company_user)
        Portfolio.objects.create(owner= Company.objects.all()[0].user)#, name= 'company_master_portfolio', cash= 100 000 000, )
        context_processors.company_settings(None)

    def test_valid_client_external_cash_deposit(self):
        print("(start test_valid_client_external_cash_deposit)")
        user = User(is_client= True, password= '12345', username= 'client1', email= 'client1@gmail.com')
        user.save()
        client = Client.objects.create(user= user)
        
        # start client portfolio with 0 in cash
        client_portfolio = Portfolio.objects.create(owner= client.user, cash= 0, name= 'first')

        # deposit 100 thousand USD
        ctr = CashTransactionRecord(
            portfolio= client_portfolio,
            status= 'processing',
            currency_type= 'USD',
            amount= self.CLIENT_START_CASH,
            amount_in_USD= self.CLIENT_START_CASH,
            transaction_type= 'external_deposit',
            transaction_to= 'self',
            transaction_from= 'somewhere',
            transaction_conditions= '0'
        )
        ctr.save()
        print(ctr.status)
        self.assertEqual(client_portfolio.cash, self.CLIENT_START_CASH)
        print("(successfully saved 10 thousand USD deposit to client's portfolio.)")

    def test_valid_client_external_cash_withdrawal(self):
        print("(start test_valid_client_external_cash_withdrawal)")
        user = User(is_client= True, password= '12345', username= 'client1', email= 'client1@gmail.com')
        user.save()
        client = Client.objects.create(user= user)
        
        # start client portfolio with 0 in cash
        client_portfolio = Portfolio.objects.create(owner= client.user, cash= 0, name= 'first')

        # deposit 100 thousand USD
        ctr = CashTransactionRecord(
            portfolio= client_portfolio,
            status= 'processing',
            currency_type= 'USD',
            amount= self.CLIENT_START_CASH,
            amount_in_USD= self.CLIENT_START_CASH,
            transaction_type= 'external_deposit',
            transaction_to= 'self',
            transaction_from= 'somewhere',
            transaction_conditions= '0'
        )
        ctr.save()
        print(ctr.status)
        self.assertEqual(client_portfolio.cash, self.CLIENT_START_CASH)
        print("(successfully saved 10 thousand USD deposit to client's portfolio.)")

        ctr = CashTransactionRecord(
            portfolio= client_portfolio,
            status= 'processing',
            currency_type= 'USD',
            amount= 1000,
            amount_in_USD= 1000,
            transaction_type= 'external_withdrawal',
            transaction_to= 'somewhere',
            transaction_from= 'self',
            transaction_conditions= '0'
        )
        ctr.save()
        print(ctr.status)
        #print(ctr.transaction_conditions)
        self.assertEqual(client_portfolio.cash, self.CLIENT_START_CASH - 1000)
        print("(successfully withdrew 1000 USD from client's portfolio.)")