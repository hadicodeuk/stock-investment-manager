import requests
import urllib
import re
import pandas as pd
import datetime
import time
from bs4 import BeautifulSoup
import numpy as np

list_shares_USD=['WBA','BABA','INTC','COIN','BLDP','OTLY','SLB','PTR','PYPL','BBLN']
exchange_rate=1.23


def convert_usd_gbp(value, exchange_rate):
    return value/exchange_rate


def return_date(date_str):

    list_date_parts=date_str.split('/')

    day=int(list_date_parts[0])
    month=int(list_date_parts[1])

    if len(list_date_parts[2])==2:
        year=2000+int(list_date_parts[2])

    else:
        year=int(list_date_parts[2])

    return datetime.date(year,month,day)

def transactions_process(df_transactions):
    df_mapping_file=pd.read_csv('./input/stock_mapping_file.csv')
    df_transactions=df_transactions.merge(df_mapping_file,on='Ticker', how='left')

    df_transactions['Price']=df_transactions['Total']/df_transactions['Number']
    df_transactions=df_transactions[df_transactions['Date'].notnull()]
    df_transactions['Date_dt']=df_transactions['Date'].apply(return_date)
    df_transactions['Type']=np.where(df_transactions['Ticker']!='Cash','Share','Cash')

    return df_transactions

def get_share_summary(df_transactions):
    
    net_cash_remaining=get_cash_remaining(df_transactions)

    shares=df_transactions[df_transactions['Type']=='Share']['Code'].unique().tolist()

    dict_stocks={}

    for share in shares:

        link=df_transactions[df_transactions['Code']==share]['Link'].min()
        ticker=df_transactions[df_transactions['Code']==share]['Ticker'].min()
        ticker_latest_price=get_price_local(share,link,exchange_rate)
        dict_stocks[ticker]=obtain_single_investment_dict(share,ticker,df_transactions,ticker_latest_price)
        time.sleep(0.1)

    shares_total_value=0
    shares_total_in=0

    for key,value in dict_stocks.items():
        shares_total_value=shares_total_value+float(value['code_value'])
        shares_total_in=shares_total_in+float(value['code_in'])

    money_change_shares=shares_total_value-shares_total_in
    pct_shares=money_change_shares/shares_total_in*100

    total_value_plus_cash=shares_total_value+net_cash_remaining

    dict_data={
                'shares_total_value':str("{:.1f}".format(shares_total_value)),
                'shares_in':str("{:.1f}".format(shares_total_in)),
                'pct_shares':str("{:.1f}".format(pct_shares)),
                'money_change_shares':str("{:.1f}".format(money_change_shares)),
                'net_cash_remaining':str("{:.1f}".format(net_cash_remaining)),
                'total_value_plus_cash':str("{:.1f}".format(total_value_plus_cash)),
                'individual_tickers':dict_stocks}

    return dict_data

def obtain_single_investment_dict(code,ticker,df_transactions,code_latest_price):


    code_cash_in=df_transactions[(df_transactions['Code']==code)&(df_transactions['Action']=='Buy')]['Total'].sum()
    code_cash_out=df_transactions[(df_transactions['Code']==code)&(df_transactions['Action']=='Sell')]['Total'].sum()
    code_in=code_cash_in-code_cash_out

    code_amount_purchased=df_transactions[(df_transactions['Code']==code)&(df_transactions['Action']=='Buy')]['Number'].sum()
    code_amount_sold=df_transactions[(df_transactions['Code']==code)&(df_transactions['Action']=='Sell')]['Number'].sum()
    code_amount=code_amount_purchased-code_amount_sold

    code_value=code_latest_price*code_amount

    money_change_code=code_value-code_in

    if code_amount>0:
        pct_code=money_change_code/code_in*100
        pct_code=str("{:.1f}".format(pct_code))
    else:
        pct_code='not applicable'

    if code_amount>0:
        code_avg_buy_price=code_in/code_amount
        code_avg_buy_price=str("{:.2f}".format(code_avg_buy_price))

    else:
        code_avg_buy_price='not applicable'

    dict_data={'code_latest_price':str("{:.2f}".format(code_latest_price)),
                'code_value':str("{:.1f}".format(code_value)),
                'code_in':str("{:.1f}".format(code_in)),
                'pct_code':pct_code,
                'money_change_code':str("{:.1f}".format(money_change_code)),
                'code_amount':str("{:.7f}".format(code_amount)),
                'code_avg_buy_price':code_avg_buy_price,
                'code':code,
                'ticker':ticker}

    return dict_data

def get_cash_remaining(df_transactions):
    cash_in=df_transactions[(df_transactions['Type']=='Cash') & (df_transactions['Action']=='In')]['Total'].sum()
    cash_out=df_transactions[(df_transactions['Type']=='Cash') & (df_transactions['Action']=='Out')]['Total'].sum()
    cash_in_sales=df_transactions[(df_transactions['Action']=='Sell')]['Total'].sum()
    cash_buying=df_transactions[(df_transactions['Action']=='Buy')]['Total'].sum()

    net_cash_remaining=cash_in+cash_in_sales-cash_buying-cash_out

    return net_cash_remaining

def get_price_local(share,link,exchange_rate):

    if share in list_shares_USD:
        lse_response=return_price_yahoo(share)

    else:
        lse_response=get_price_lse(link)/100

    if lse_response==-1:
        api_response=price_ticker(share)

        if api_response==-1:
            return 'Cannot get the share prices'

        else:
            ticker_latest_price=api_response/100

    else:
        ticker_latest_price=lse_response

    if share in list_shares_USD:
        ticker_latest_price=convert_usd_gbp(lse_response,exchange_rate)

    return ticker_latest_price

def get_price_lse(link):

    """
    Function to scrape price of stock from website provided
    """

    f = urllib.request.urlopen(link)
    website_text = f.read()
    regex_search = re.search(r'class="price-tag"><!----><!---->(\d+.\d+)', str(website_text))

    if regex_search is None:
        return -1

    else:
        str_price=regex_search.group(1)

        str_price_clean=str_price.replace(',','')
        num_price_clean=float(str_price_clean)
        return num_price_clean

def return_price_yahoo(share):
    url = 'https://finance.yahoo.com/quote/'+ share + '/key-statistics?p=' + share

    request=urllib.request.Request(url)
    request.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36')
    page=urllib.request.urlopen(request)
    soup = BeautifulSoup(page, 'lxml')
    close_price = [entry.text for entry in soup.find_all('fin-streamer', {'class':'Fw(b) Fz(36px) Mb(-4px) D(ib)'})]

    if isinstance(close_price[0],str):

        if len(close_price[0])>=1:
            close_price=float(close_price[0])

        else:
            close_price=np.NaN

    return close_price
