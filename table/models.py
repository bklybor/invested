import datetime
import pandas as pd
import uuid
import pytz

from django.db.models import *
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
 

from home.models import Client, Broker, User



# 1: python manage.py makemigrations
# 2: python manage.py migrate

default_date = datetime.datetime(1,1,1,0,0,0, tzinfo=datetime.timezone.utc)
decimal_places = 6

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

    owner = ForeignKey(Client, on_delete= CASCADE, related_name='portfolios')
    name = CharField(max_length= 255, default= '')
    open_date = DateTimeField(auto_now_add= True)
    close_date = DateTimeField(default= default_date, blank= True)
    cash = DecimalField(max_digits= 20, decimal_places= decimal_places, default= 0)
    description = CharField(max_length= 1000, default= '')

    def get_full_transact_field_names(self):
        """Get all field names for StockTransactRecord."""
        cols = [f.name for f in StockTransactRecord._meta.fields]
        if (cols is None) or (not cols):
            raise Exception("Retrieval of field names failed")
        return cols

    def get_unique_transact_field_names(self):
        """Get all field names for StockTransactRecord except for foreign key and id columns."""
        cols = [f.name for f in StockTransactRecord._meta.fields if f.name != 'id' and not isinstance(f, ForeignKey)]
        if (cols is None) or (not cols):
            raise Exception("Retrieval of field names failed")
        return cols

    def get_unique_transact_fields(self):
        return self.stocktransactrecord_set.all().values_list(*self.get_unique_transact_field_names())

    def get_full_transact_fields(self):
        return self.stocktransactrecord_set.all().values_list(*self.get_full_transact_field_names())

    def get_self(self):
        """Get all stock transactions associated with this instance's portfolio."""
        return self.stocktransactrecord_set.all()

    def get_stocks_value(self):
        values = self.stocktransactions.annotate(value= ExpressionWrapper(F('price') * F('quantity'), output_field=FloatField()))

    def get_value(self):
        # total value of sell orders
        sell_value = self.stocktransactions \
        .annotate(value= ExpressionWrapper(F('price') * F('quantity'), output_field=DecimalField(max_digits= 20, decimal_places= 2))) \
        .filter(transaction_type= 'sell') \
        .aggregate(Sum('value'))

        # total value of but orders
        buy_value = self.stocktransactions \
        .annotate(value= ExpressionWrapper(F('price') * F('quantity'), output_field= DecimalField(max_digits= 20, decimal_places= 2))) \
        .filter(transaction_type= 'buy') \
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
    price = DecimalField(max_digits= 50, decimal_places= decimal_places, default= 0)
    logo = CharField(max_length= 1000, default= '')
    date = DateTimeField(default= default_date)

    def get_stocks_data(tickers=['^DJI', '^GSPC', '^IXIC'], dates= ['2000-01-01', '2020-01-01']):
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
            prices_percent_change.insert(0, ticker)
            prices_list.append(prices_percent_change)

            

        return [prices_list, dates]


    class Meta:
        unique_together = [['ticker', 'date']]

class StockTransactRecord(Model):
    """Records the buy and/or sell order on a given stock for a given portfolio.
    
    :param portfolio: the associated Portfolio
    :type portfolio: table.models.Portfolio
    
    :param exchange_abbr: abbreviation for the stock exchange the transaction took place on
    :type exchange_abbr: str

    :param ticker: the ticker symbol for the stock for the transaction
    :type ticker: str

    :param buy_date: the buy date and time for the transaction in UTC
    :type buy_date: datetime.datetime

    :param sell_date: the sell date and time for the transaction in UTC
    :type sell_date: datetime.datetime

    :param buy_price: the buy price in USD
    :type buy_price: decimal

    :param sell_price: the sell price in USD
    :type sell_price: decimal
    """
    portfolio = ForeignKey(Portfolio, on_delete= CASCADE, related_name= 'stocktransactions')
    exchange_abbr = CharField(max_length= 50, default= '', blank= True)
    ticker = CharField(max_length= 50, default= '', blank= True)
    transaction_type = CharField(max_length= 100, default= '', blank= True)
    transaction_date = DateTimeField(default= default_date, blank= True)
    price = DecimalField(max_digits= 50, decimal_places=decimal_places, default= 0, blank= True)
    quantity = PositiveIntegerField(default= 0, blank= True)
    timestamp = DateTimeField(auto_now_add= True)
    id = UUIDField(primary_key= True, default=uuid.uuid4, editable=False)

    def __str__(self):
        return str(self.timestamp)

    def get_id(self):
        return str(self._id.uuid4().hex)

    def get_field_names(self):
        return [f.name for f in self._meta.fields]
