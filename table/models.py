import datetime
import pandas as pd
import uuid
import pytz
from enum import Enum

from django.db.models import *
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.db.models.signals import post_save, post_init, pre_save
from django.dispatch import receiver

from home.models import Client, Broker, User, Company
from settings.models import SiteSettings, StockManagementSettings

default_date = datetime.datetime(1,1,1,0,0,0, tzinfo=datetime.timezone.utc)
decimal_places = 6
date_format = '%Y-%m-%d %H:%M:%S'

site_settings = SiteSettings.objects.all()[0]
stock_managment_settings = list(StockManagementSettings.objects.values())[0]
stock_managment_settings.pop('id') # dictionary of settings
company = Company.objects.all()[0]

class Portfolio(Model):
    """A model representing a portfolio for a given client.
    
    :param owner: the owner of this portfolio
    :type owner: home.models.User
    
    :param name: the name of the portfolio
    :type name: str

    :param current_value: the current value of the portfolio in USD
    :type current_value: Decimal

    :param percent change: the to-date percent change in portfolio value
    :type percent_change: Decimal

    :param open_date: the date in UTC this portfolio was opened
    :type open_date: datetime.datetime

    :param close_date: the date in UTC this portfolio was closed
    :type close_date: datetime.datetime
    """

    owner = ForeignKey(User, on_delete= CASCADE, related_name='portfolios')
    name = CharField(
        max_length= 255, 
        default= '',
        help_text= 'A nickname for this portfolio')
    open_date = DateTimeField(auto_now_add= True)
    close_date = DateTimeField(default= site_settings.db_default_date, blank= True)
    cash = DecimalField(
        max_digits= 20, 
        decimal_places= site_settings.monetary_decimal_places, 
        default= 0,
        help_text= 'The amount of cash in USD held in this portfolio.')
    description = CharField(
        max_length= 1000, 
        default= '',
        help_text= 'A brief description of this portfolio.')
    portfolio_id = UUIDField(default=uuid.uuid4, editable=False)

    @classmethod
    def get_field_names(cls):
        return [f.name for f in cls._meta.fields]

    def get_stocks_info(self):
        values = []
        for transaction in self.stocktransactions.all():
            values.append(float(transaction.get_value()))
        '''list(self.stocktransactions.annotate(value= ExpressionWrapper(F('price') * F('quantity'), output_field=FloatField())).values('value', 'price'))'''
        #values_list = [value['value'] for value in values]
        prices_list = list(self.stocktransactions.all().values('price'))
        prices = [float(value['price']) for value in prices_list]
        
        quantities_list = list(self.stocktransactions.all().values('quantity'))
        quantities = [value['quantity'] for value in quantities_list]

        types_list = list(self.stocktransactions.all().values('order_type'))
        types = [value['order_type'] for value in types_list]
        
        return [prices, quantities, values, types]

    def get_value(self, date= datetime.datetime.now()):
        """Get the value of this portfolio at a given datetime.
        
        :param date: the date to calculate the value for, defaults to dateime.datetime.now()
        :type date: datetim.datetime, with tzinfo= datetime.timezone.utc

        :return: monetary value of this portfolio on the given date in USD
        :rtype: Decimal
        """
        # total value of sell orders
        sell_value = self.stocktransactions \
        .annotate(value= ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField(max_digits= 20, decimal_places= site_settings.monetary_decimal_places))) \
        .filter(order_type= 'sell') \
        .aggregate(Sum('value'))

        # total value of but orders
        buy_value = self.stocktransactions \
        .annotate(value= ExpressionWrapper(F('price') * F('quantity'), output_field= DecimalField(max_digits= 20, decimal_places= site_settings.monetary_decimal_places))) \
        .filter(order_type= 'buy') \
        .aggregate(Sum('value'))

        buy_value = buy_value['value__sum'] if buy_value['value__sum'] else 0
        sell_value = sell_value['value__sum'] if sell_value['value__sum'] else 0
        total_value = buy_value - sell_value + self.cash

        return total_value  

    def __str__(self):
        return self.name

class Stock(Model):
    """
    Table storing stock information for a given date and time of a given stock.
    """
    exchange_abbr = CharField(max_length= 100, default= '')
    exchange_long = CharField(max_length= 100, default= '')
    ticker = CharField(max_length= 100, default= '')
    name = CharField(max_length= 200, default= '')
    summary = CharField(max_length= 1000, default= '')
    price = DecimalField(
        max_digits= 50, 
        decimal_places= site_settings.monetary_decimal_places, 
        default= 0
    )
    logo = CharField(max_length= 1000, default= '')
    date = DateTimeField(default= site_settings.db_default_date)

    class Meta:
        unique_together = [['ticker', 'date']]

    @classmethod
    def get_quote(cls, exchange_abbr='', ticker='^DJI', date_and_time='2000-01-03 00:00:00'):
        """
        Get the price of a stock at a give datetime

        :param exchange_abbr: the exchange abbreviation, default is, ''
        :type exchange_abbr: str

        :param ticker: the ticker to lookup, default is '^DJI'
        :type ticker: str

        :param datetime: the time in UTC at which to find the stock price, default is '2000-01-03 00:00:00'
        :type date_and_time: str

        :return: the price of the given stock at the given date and time
        :rtrype: Decimal
        """
        
        date = pytz.utc.localize(datetime.datetime.strptime(date_and_time, date_format))
        print(date, ticker, exchange_abbr)
        try:
            return cls.objects.get(ticker= ticker, date= date, exchange_abbr= exchange_abbr).price
        except Stock.DoesNotExist:
            return -1

    @classmethod
    def get_stocks_data(cls, tickers=['^DJI', '^GSPC', '^IXIC'], dates= ['2000-01-01', '2020-01-01']):
        """
            Retrieves stock data from internally stored Stock table.

            :param tickers: the list of stock tickers to retrieve, defaults to ['^DJI','^GSPC','^IXIC']
            :type tickers: list

            :param dates: range of dates in the format 'YYYY-DD-MM', defaults to ['2000-01-01', '2020-01-01']
            :type dates: list

            :return: a list containin 1.) a list of prices for each ticker that begins with the ticker symbot, 2.) a list of dates
            :rtype: list
        """
        start_date = pytz.utc.localize(datetime.datetime.strptime(dates[0], '%Y-%m-%d'))
        end_date = pytz.utc.localize(datetime.datetime.strptime(dates[1], '%Y-%m-%d'))


        prices_list = []
        # find all stock prices in the given range
        for ticker in tickers:
            dates = pd.date_range(start= start_date, end= end_date).to_pydatetime().tolist()
            dates = [x.strftime('%Y-%m-%d') for x in dates]
            

            date_prices = Stock.objects.filter(Q(ticker= ticker))
            d = date_prices[0].date
            date_prices = date_prices.filter(date__range=(start_date, end_date))
            date_prices = date_prices.order_by('-date')
            date_prices = date_prices.values_list('date', 'price')
            date_prices = list(date_prices)
            
            
            stock_prices = [float(x[1]) for x in date_prices]
            stock_dates = [x[0].strftime('%Y-%m-%d') for x in date_prices]
            date_prices = {stock_dates[i]: stock_prices[i] for i in range(len(stock_prices))}
            all_prices = []
            # if the date in stock_dates also exists in the date range 
            # append the price for this stock on this date 
            # otherwise append a null value
            for date in dates:
                if date in stock_dates:
                    all_prices.append(date_prices[date])
                else:
                    all_prices.append(None)
            

            start_price = next(num for num in all_prices if num is not None)
            prices_percent_change = []
            for price in all_prices:
                if price is not None:
                    prices_percent_change.append((price / start_price)-1)
                else:
                    prices_percent_change.append(price)
            
            # prepend the ticker symbol to each price list
            #prices_percent_change.insert(0, ticker)
            all_prices.insert(0, ticker)
            prices_list.append(all_prices)

        return [prices_list, dates]

class StockTransactRecord(Model):
    """Records the buy and/or sell order for a given stock for a given portfolio.
    
    :param portfolio: the associated Portfolio
    :type portfolio: table.models.Portfolio
    
    :param exchange_abbr: abbreviation for the exchange
    :type exchange_abbr: str

    :param ticker: the ticker symbol for the stock for the order
    :type ticker: str

    :param order_type: the order type, default is 'buy'
    :type order_type: str

    :param order_palacement_datetime: order placement time in UTC
    :type order_placement_datetime: datetime.datetime

    :param order_execution_datetime: order placement time in UTC
    :type order_execution_datetime: datetime.datetime

    :param price: the transaction price in USD
    :type price: Decimal

    :param quantity: quantity of stocks for the order
    :type quantity: PositiveInteger
    """

    class TRANSACTION_TYPE(Enum):
        buy = ('buy', 'Stock buy order.')
        sell = ('sell', 'Stock sell order.')

        @classmethod
        def get_value(cls, member):
            return cls[member].value[0]

    class STATUS(Enum):
        approved = ('approved', 'Order passes automatic checks.')
        rejected = ('rejected', 'Order cannot be processed.')
        processing = ('processing', 'Order is currently processing.')
        under_review = ('under_review', 'Order is currently under review.')

        @classmethod
        def get_value(cls, member):
            return cls[member].value[0]

    class TRANSACTION_CLASS(Enum):
        internal = ('internal', 'This is an internal order.')
        external = ('external', 'This is an external order.')
        split = ('split', 'This order has been split into an external order and an internal order.')
        undetermined = ('undetermined', 'The class of this order has not yet been determined.')
        @classmethod
        def get_value(cls, member):
            return cls[member].value[0]

    portfolio = ForeignKey(
        Portfolio, 
        on_delete= CASCADE, 
        related_name= 'stocktransactions'
    )
    exchange_abbr = CharField(max_length= 50, default= '', blank= True)
    ticker = CharField(max_length= 50, default= '', blank= True)
    order_type = CharField(
        max_length= 50, 
        choices= [x.value for x in TRANSACTION_TYPE], 
        default= TRANSACTION_TYPE.get_value('buy'), 
        blank= True
    )
    order_placement_datetime = DateTimeField(
        default= site_settings.db_default_date,
        blank= True,
        help_text= 'The datetime in UTC the order was placed.')
    order_execution_datetime = DateTimeField(
        default= site_settings.db_default_date, 
        blank=True,
        help_text= 'The datetime in UTC the order was executed')
    price = DecimalField(
        max_digits= 50, 
        decimal_places= site_settings.monetary_decimal_places, 
        default= 0, 
        blank= True
    )
    quantity = PositiveIntegerField(default= 0, blank= True)
    order_status = CharField(
        max_length= 50,
        choices= [x.value for x in STATUS], 
        default= STATUS.get_value('processing'), 
        blank= True
    )
    order_class = CharField(
        max_length= 50,
        choices= [x.value for x in TRANSACTION_CLASS], 
        default= TRANSACTION_CLASS.get_value('undetermined'), 
        blank= True
    )
    broker_review_requested = BooleanField(
        default= False,
        help_text= 'Indicates whether or not the user has requested this order to be manually reviewed by a broker.')
    message = CharField(max_length=1200, default='', blank= True)
    timestamp = DateTimeField(auto_now_add= True)
    order_id = CharField(max_length= 50, default='', blank= True)
    order_part_of = ForeignKey(
        'self', 
        on_delete= CASCADE,
        blank= True,
        null= True
    )
    transaction_id = UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return str(self.timestamp)

    def get_id(self):
        return str(self._id.uuid4().hex)

    @classmethod
    def get_field_names(cls):
        return [f.name for f in cls._meta.fields]

    def get_value(self):
        return self.price * self.quantity

'''@receiver(post_save, sender= StockTransactRecord, dispatch_uid= 'stock_transaction_post_save')
def stock_transaction_post_save(sender, instance, **kwargs):
    if instance.order_status == StockTransactRecord.STATUS.approved.name:
        sign = 0
        if instance.order_type == StockTransactRecord.TRANSACTION_TYPE.buy.name:
            print('(Taking cash from portfolio to cover buy order.)')
            sign = -1
        if instance.order_type == StockTransactRecord.TRANSACTION_TYPE.sell.name:
            print('(Depositing cash from sell order.)')
            sign = 1
        else:
            # throw some kind of error
            pass

        instance.portfolio.cash += (sign * instance.price * instance.quantity)
        instance.portfolio.save()'''

@receiver(pre_save, sender= StockTransactRecord, dispatch_uid= 'stock_transaction_pre_save')
def stock_transaction_pre_save(sender, instance, **kwargs):
    #if order.feature_1 > some_threshold:
    #   order.status = STATUS.under_review
    #   broker.orders_to_review.append(order)
    #elif order.feature_2 > some_other_threshold:
    #   order.status = STATUS.under_review
    #   broker.orders_to_review.append(order)
    #elif ...
    #else:
    #   if order.value > portfolio.cash:
    #       raise ValueError

    # only proceed if the order has not yet been processed
    print('(Start processing of order.)')
    if instance.order_status == StockTransactRecord.STATUS.processing.name:
        print('(Order processing start.)')
        if instance.order_type == StockTransactRecord.TRANSACTION_TYPE.buy.name:
            print("(Processing buy order.)")
            if instance.broker_review_requested:
                print('(Buy order sent for manual review.)')
                instance.order_status = StockTransactRecord.STATUS.under_review.name
                # add order to broker's review list
            else:
                is_internal_order = instance.order_class == StockTransactRecord.TRANSACTION_CLASS.internal.name
                is_undetermined_order = instance.order_class == StockTransactRecord.TRANSACTION_CLASS.undetermined.name
                
                if is_internal_order or is_undetermined_order:
                    print('(Processing internal or undetermined order.)')
                    tickers = [x[0] for x in company.user.portfolios.all()[0].stockinventory.all().values_list('ticker').distinct()]
                    is_in_inventory = instance.ticker in tickers
                    
                    if is_in_inventory:
                        print('(Requested stock is in internal inventory.)')
                        # get number of shares in company inventory for this ticker
                        shares_in_inventory = company.user.portfolios.all()[0].stockinventory.get(ticker= instance.ticker).quantity
                        if instance.quantity <= shares_in_inventory :
                            print('(Requested quantity is in internal inventory.)')
                            instance.order_class = StockTransactRecord.TRANSACTION_CLASS.internal.name
                            is_internal_share_proportion_ok = (instance.quantity/ shares_in_inventory) < stock_managment_settings['internal_share_proportion_threshold']
                            is_internal_value_ok = (instance.price * instance.quantity) < stock_managment_settings['internal_value_threshold']
                            if is_internal_share_proportion_ok and is_internal_value_ok:
                                print('(Order passes internal checks, adding order to internal order aggregator)')
                                instance.order_status = StockTransactRecord.STATUS.approved.name
                                instance.message = 'Order within internal threholds and approved for execution.'
                                # add order to internal order aggregator
                            else:
                                print('(Order fails internal checks, labelling for review.)')
                                instance.order_status = StockTransactRecord.STATUS.under_review.name
                                instance.mesage = 'Order under review for exceeding internal thresholds.'
                                # add order to broker's review list

                            instance.save()
                        else: # if requested purchase order quantity is over amount in inventory
                            print('Order exceeds number of shares available internally, splitting order into internal and external order.')
                            internal_quantity = shares_in_inventory
                            external_quantity = instance.quantity - shares_in_inventory
                            
                            internal_order = StockTransactRecord(
                                portfolio = instance.portfolio,
                                order_type= instance.order_type,
                                exchange_abbr= instance.exchange_abbr,
                                ticker= instance.ticker,
                                price= instance.price,
                                order_placement_datetime= instance.order_placement_datetime,
                                order_execution_datetime= instance.order_execution_datetime,
                                quantity= internal_quantity,
                                order_status= '',
                                order_class= StockTransactRecord.TRANSACTION_CLASS.internal.name,
                                broker_review_requested= False,
                                message= 'This is the internally executable part of a split order.',
                                order_part_of= instance
                            )
                            internal_order.save()

                            external_order = StockTransactRecord(
                                portfolio = instance.portfolio,
                                order_type= instance.order_type,
                                exchange_abbr= instance.exchange_abbr,
                                ticker= instance.ticker,
                                price= instance.price,
                                order_placement_datetime= instance.order_placement_datetime,
                                order_execution_datetime= instance.order_execution_datetime,
                                quantity= internal_quantity,
                                order_status= '',
                                order_class= StockTransactRecord.TRANSACTION_CLASS.external.name,
                                broker_review_requested= False,
                                message= 'This is the externally executable part of a split order.',
                                order_part_of= instance
                            )
                            external_order.save()

                            instance.order_class = StockTransactRecord.TRANSACTION_CLASS.split.name
                            instance.save()
                    else: # if ticker isn't in inventory, change order class to external
                        print('Requested stock isn\'t in internal inventory, creating external order.)')
                        instance.order_class = StockTransactRecord.TRANSACTION_CLASS.external.name
                        instance.save()
                        
                elif instance.order_class == StockTransactRecord.TRANSACTION_CLASS.external.name: # if order is external
                    
                    # need to add table with stock-specific info like shares outstanding
                    # for now just assume that shares outstanding is 10000000 for each
                    # stock
                    is_external_share_proportion_ok = (instance.quantity/ 10000000) < stock_managment_settings['external_share_proportion_threshold']
                    is_external_value_ok = (instance.price * instance.quantity) < stock_managment_settings['external_value_threshold']
                    if is_external_share_proportion_ok and is_external_value_ok:
                        print('(Order passes external checks, adding order to external order aggregator.)')
                        instance.order_status = StockTransactRecord.STATUS.approved.name
                        instance.message = 'Order within external thresholds and approved for execution.'
                        # add order to external order aggregator
                    else:
                        print('(Order fails external checks, labelling for manual review.)')
                        instance.order_status = StockTransactRecord.STATUS.under_review.name
                        instance.message = 'Order under review for exceeding external thresholds.'
                        # add order to broker's review list
                    instance.save()
                    # from table.models import StockTransactRecord, Portfolio
                    # p = Portfolio.objects.get(name='first')
                    # st = StockTransactRecord(portfolio= p, ticker= 'IBM', exchange_abbr= 'NYSE', order_type= 'buy', order_class= 'undetermined', price= 100, quantity= 100)
                    # st.save()
                    # 
                elif instance.order_class == StockTransactRecord.TRANSACTION_CLASS.split.name:
                    print('(This is a split order.)')

        else:
            print('(Sell function not supported yet)')
    elif instance.order_status == StockTransactRecord.STATUS.approved.name:
        sign = 0
        if instance.order_type == StockTransactRecord.TRANSACTION_TYPE.buy.name:
            print('(Taking cash from portfolio to cover buy order.)')
            sign = -1
        if instance.order_type == StockTransactRecord.TRANSACTION_TYPE.sell.name:
            print('(Depositing cash from sell order.)')
            sign = 1
        else:
            # throw some kind of error
            pass

        instance.portfolio.cash += (sign * instance.price * instance.quantity)
        instance.portfolio.save()

class StockInventory(Model):
    """
    A table that keeps track of the quantity of each stock in each portfolio.

    :param portfolio: the portfolio that this inventory belongs to
    :type portfolio: Portfolio

    :param exchange_abbr: the exchange abbreviation
    :type exchange_abbr: str

    :param ticker: the stock ticker
    :type ticker: str

    :param quantity: amount of shares owned
    :type quantity: PositiveInteger

    :param ownership_type: the type of ownership, default 'long'
    :type ownership_type: str
    """

    portfolio = ForeignKey(Portfolio, on_delete=CASCADE, related_name='stockinventory')
    exchange_abbr = CharField(max_length= 50, default= '', blank= True)
    ticker = CharField(max_length= 50, default= '', blank= True)
    quantity = PositiveIntegerField(default= 0, blank= True)

    def __str__(self):
        return self.exchange_abbr + ' ' + self.ticker + ' ' + str(self.quantity)

class CashTransactionRecord(Model):
    """
    A Record of monetary transactions associtated with a give portfolio.
    """
    class TRANSACTION_TYPE(Enum):
        deposit = ('deposit', 'Cash deposit in to the associated Portfolio.')
        withdrawal = ('withdrawal', 'Cash withdrawal from the associated Portfolio.')

        @classmethod
        def get_value(cls, member):
            return cls[member].value[0]

    class CURRENCY_TYPE(Enum):
        USD = ('USD', 'United States Dollar')
        EUR = ('EUR', 'European Euro')
        GBP = ('GBP', 'British Pound')
        JPY = ('JPY', 'Japanese Yen')
        CAD = ('CAD', 'Canadian Dollar')
        CHF = ('CHF', 'Swiss Franc')

        @classmethod
        def get_value(cls, member):
            return cls[member].value[0]

    transaction_id = UUIDField(primary_key= True, default=uuid.uuid4, editable=False)
    portfolio = ForeignKey(
        Portfolio, 
        on_delete= CASCADE, 
        related_name= 'cashtransactions'
    )                    
    currency_type = CharField(
        max_length= 10, 
        choices=[x.value for x in CURRENCY_TYPE], 
        default= CURRENCY_TYPE.get_value('USD'), 
        blank= True
    )
    amount = DecimalField(
        max_digits= 50, 
        decimal_places= site_settings.monetary_decimal_places, 
        default= 0, 
        blank= True
    )
    transaction_type = CharField(
        max_length= 20, 
        choices=[x.value for x in TRANSACTION_TYPE], 
        default= TRANSACTION_TYPE.get_value('deposit'), 
        blank= True
    )
    transaction_to = CharField(max_length= 50, default= '', blank= True)
    transaction_from = CharField(max_length= 50, default= '', blank= True)
    transaction_datetime = DateTimeField(default= site_settings.db_default_date, blank=True)

    def __str__(self):
        return str(self.id)

#---CashTransactionRecord Signals---#
@receiver(post_save, sender= CashTransactionRecord, dispatch_uid= 'portfolio_cash_transaction')
def portfolio_cash_transaction(sender, instance, **kwargs):
    """
    Updates the cash amount in a portfolio after a cash deposit or withdrawal is sucessfully saved.
    """
    sign = 0
    if instance.transaction_type == CashTransactionRecord.TRANSACTION_TYPE.deposit.name:
        sign = 1
    elif instance.transaction_type == CashTransactionRecord.TRANSACTION_TYPE.withdrawal.name:
        sign = -1
    else:
        # should throw some kind of error, or handle special cases, but pass for now
        pass
    
    # if the currency type is USD, update cash, otherwise convert
    if instance.currency_type == CashTransactionRecord.CURRENCY_TYPE.USD.name:
        instance.portfolio.cash += (sign * instance.amount)
    else:
        # do some conversion into USD
        pass


