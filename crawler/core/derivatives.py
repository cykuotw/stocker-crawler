# coding=utf-8
import time
from io import StringIO

import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def crawlStockFuture():
    """
    @Description:
        Crawl stock list with derivatives such as option and future
    @Parameter:
        N/A
    @Return:
        Dataframe (stock id, future exist, option exist, share represented)
    """
    data = requests.get(
        "https://www.taifex.com.tw/cht/2/stockLists")
    dfs = pd.read_html(StringIO(data.text), converters={'證券代號': str})
    dfs[1].columns = dfs[1].columns.str.replace(' ', '')
    return dfs[1][["證券代號", "是否為股票期貨標的", "是否為股票選擇權標的", "標準型證券股數/受益權單位"]]


def crawlVolatility() -> dict:
    option = webdriver.ChromeOptions()
    option.add_argument('--headless')
    option.add_argument('--disable-gpu')
    service_object = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service_object, options=option)
    driver.get(
        "https://mis.taifex.com.tw/futures/RegularSession/EquityIndices/FuturesDomestic/")
    time.sleep(2)
    driver.find_element(By.CLASS_NAME, 'btn').click()
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()
    td = soup.find_all("tbody")[0].find_all("tr")[1].find_all("td")
    difference = float(td[11].text.replace(',', '')) - \
        float(td[12].text.replace(',', ''))

    message = {
        '商品': td[0].text.strip(),
        '成交價': td[6].text,
        '漲跌': td[7].text,
        '震幅': td[8].text,
        '點數差': str(difference),
        '最高': td[11].text,
        '最低': td[12].text
    }

    return message
