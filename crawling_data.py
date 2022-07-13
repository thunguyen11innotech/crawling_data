    # -*- coding: utf-8 -*-

from concurrent.futures import ThreadPoolExecutor as PoolExecutor
from ratelimit import limits, sleep_and_retry

import urllib.request as openurl
# ssl._create_default_https_context = ssl._create_unverified_context
from bs4 import BeautifulSoup
import pandas as pd
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


    # code fix
def get_tickers():
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

TEN_MINUTES = 60
@sleep_and_retry
@limits(calls=10, period=TEN_MINUTES)

def data_tickers(ticker):

    sticker_test = (
        "https://hnx.vn/cophieu-etfs/chi-tiet-chung-khoan-uc-%s.html?_des_tab=1"
        % ticker
    )

    # with openurl.urlopen(sticker_test,timeout=1000) as url:
    #  r = url.read()
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
    return data

if __name__ == "__main__":
	column = (['Mã CK', 'Tên TCPH', 'Trụ sở chính', 'Số điện thoại ', 'GPTL/ĐKKD ',
	'Người đại diện pháp luật ', 'Người công bố thông tin', 'Bản cáo bạch ',
	'Trạng thái kiểm soát', 'Trạng thái giao dịch', 'Ngày GD đầu tiên ',
	'Vốn điều lệ (Nghìn đồng) ', 'KLLH (Cổ phiếu) ', 'KLĐKGD (Cổ phiếu) '])
	data_content = pd.DataFrame(columns=column)
	#data_content = pd.DataFrame(columns=["ticker", "title", "content"])
	tickers = get_tickers()
	with PoolExecutor(max_workers=5) as executor:
		for _results in executor.map(data_tickers, tickers[:15]):
			data_content = pd.concat([data_content, _results], ignore_index=True)
	data_content.columns = ['ticker','company_name','address','phone_number','licence_number','legal_representative',
	'publisher','report','control_status','trading_status','first_trading','capital','volume_share','volume_trading']
	#data_content.to_csv('data_upcom.csv',encoding='utf-8')
	print(data_content)