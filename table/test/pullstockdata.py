from datetime import datetime
import csv
import pandas as pd
from decimal import Decimal
import pytz
import random

from table.models import Stock, StockTransactRecord, Portfolio


def pull_from_csv(csv_path):
    '''Pulls from the csv given by :csv_path: and writes to the database. For now only works with csv with a schema like this:
       Date    | Ticker1 | Ticker2 | ...
    -------------------------------------
    YYYY-MM-DD |  $$$$$  |  $$$$$  | ...
    YYYY-MM-DD |  $$$$$  |  $$$$$  | ...
    YYYY-MM-DD |  $$$$$  |  $$$$$  | ...
    YYYY-MM-DD |  $$$$$  |  $$$$$  | ...

    returns a DataFram with the same schema as the csv
    '''
    
    df = pd.read_csv(csv_path)
    # convert from Timstampl to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    dates = df['Date'].dt.to_pydatetime()
    # the tickers
    tickers = df.columns[1:]
    for i, row in df.iterrows():
        # localize date to utc
        date = pytz.utc.localize(dates[i])
        for ticker in tickers:
            # if no unique ticker-date pair exists, then insert a new stock record
            if not Stock.objects.filter(ticker= ticker, date= date).exists():
                price = df.loc[i][ticker]
                if pd.notna(price):
                    stock = Stock(ticker= ticker, date= date, price= price)
                    stock.save()
    return df

def generate_random_transactions(portfolio, k=10):
    '''
    Inserts into the StockTransactRecord of the given Portfolio k number of random Stock transactions based on the historical data in the Stock table.
    '''
    

