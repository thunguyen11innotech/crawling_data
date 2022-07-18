# get ticker profile from HNX
from cProfile import label
from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from ratelimit import limits, sleep_and_retry
import urllib.request as openurl
# ssl._create_default_https_context = ssl._create_unverified_context
from bs4 import BeautifulSoup
import pandas as pd
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from datetime import date
import numpy as np
import os.path
def get_tickers():
    """_summary_

    Returns:
        tickers (list): contain all collected tickers 
    """
    html_link = "https://hnx.vn/vi-vn/cophieu-etfs/chung-khoan-uc.html"
    s = requests.get(html_link, verify=False).text
    soup = BeautifulSoup(s, "html.parser")
    data = pd.DataFrame(columns=["ticker", "company"])
    for option in soup.find_all("option"):
        data_ticker = pd.DataFrame(
            [{"ticker": option["value"], "company": option.text}]
        )
        data = pd.concat([data, data_ticker], ignore_index=True)
    tickers = data.ticker[:-5]
    return tickers.to_list()

ONE_MINUTES = 60
@sleep_and_retry
@limits(calls=30, period=ONE_MINUTES)

def ticker_information(ticker: str) -> str:
    """_summary_

    Args:
        ticker (string): ticker of company will be collected information

    Returns:
        data (DataFrame): dataframe contains information of ticker. 
    """
    sticker_test = (
        "https://hnx.vn/cophieu-etfs/chi-tiet-chung-khoan-uc-%s.html?_des_tab=1"
        % ticker
    )

    # with openurl.urlopen(sticker_test,timeout=1000) as url:
    #  r = url.read()
    try:
        r = requests.get(sticker_test, verify=False).text
        company_data = BeautifulSoup(r, "html.parser")
        data_raw_v2 = zip(
            company_data.find_all("div", {"class": "dktimkiem_cell_title"}),
            company_data.find_all("div", {"class": "dktimkiem_cell_content"})
        )
        data = pd.DataFrame([])
        for titles, contents in data_raw_v2:
            data_content_raw = pd.DataFrame(
                [{"title": titles.text, "content": contents.text}]
            )
            data = pd.concat([data, data_content_raw], ignore_index=True)
        openurl.urlcleanup()
        print("Done", ticker)
        data = data.replace(r"\n", "", regex=True)
        data = data.replace(r"\r", "", regex=True)
        data = data.T
        data.columns = data.iloc[0]
        data = data.iloc[1:].reset_index(drop=True)
        data.columns = ['ticker','company_name','address','phone_number','licence_number','legal_representative',
        'publisher','report','control_status','trading_status','first_trading','capital','volume_share','volume_trading']
        data['update_date'] = date.today()
    except:
        print(f"Error get ticker {ticker}")
        pass
    return data

def check_data(path_to_file,data_content):
    df_current_source = pd.read_csv(path_to_file,index_col='ticker')
    df_new_source = data_content
    df_new_source = df_new_source.set_index('ticker')
    idx_df = df_new_source.iloc[:,:-1].isin(df_current_source.iloc[:,:-1]).any(axis='columns') # get ticker not match values
    idxs = idx_df[idx_df == False].index # get ticker 
    print(idxs)
    # insert new row with tickers index
    for idx in idxs:
        df_current_source.loc[idx] = df_new_source.loc[idx]
    df_current_source.to_csv(path_to_file)
    print('Tickers change:', idxs.tolist())
