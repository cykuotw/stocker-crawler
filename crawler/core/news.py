# coding=utf-8
import json
from datetime import datetime, timedelta

import feedparser
import requests

from crawler.core.util import formatJSON

# export example:
# {
#     "data_count": "1",
#     "data":[
#         {
#             "link": "example.com.tw/5566789",
#             "stock_id": [
#              "2330", "2454" ...
#             ],
#             "title": "blahblahblahblah",
#             "source": "cynes",
#             "releaseTime": 1662024303 //sec from 1970/1/1
#         },
#         ...
#     ]
# }


def crawlNewsYahoo(companyID):
    """
    @Description:
        爬取Yahoo Stock個股每日新聞\n
        Crawl daily news of specific companyID form Yahoo Stock\n
        ** Under Construction **
    @Param:
        companyID => int
    @Return:
        json (see example)
    """

    coID = str(companyID)
    url = "https://tw.stock.yahoo.com/rss/s/" + coID

    res = requests.get(url)
    res.encoding = "big5"
    feed = feedparser.parse(res.text)
    for item in feed.entries:
        dateTime = datetime.strptime(item.pubDate, '%a, %d %b %Y %H:%M:%S %Z')
        print('datetime', dateTime.isoformat())
        print('title', item.title)
        print('link', item.link)
        print('description', item.description)
        print('stock_id', coID)
        print("======================================")


def crawlNewsCnyes(date=datetime.today(), market="tw"):
    """
    @Description:
        爬取鉅亨網個股每日新聞\n
        Crawl daily news of all Taiwan stocks from CNYES\n
    @Param:
        date => datetime (default: system current date)
        market => string ("tw", "us")
    @Return:
        json (see example)(empty if @Param market is neither "tw", "us")
    """

    # Check parameter
    if market != "tw" and market != "us":
        return json.dumps({})

    # generate timestamp
    epochTime = datetime(1970, 1, 1)

    todayStart = date.replace(hour=0, minute=0, second=0, microsecond=0)
    todayEnd = todayStart + timedelta(days=1)
    todayStartSec = int((todayStart-epochTime).total_seconds())
    todayEndSec = int((todayEnd-epochTime).total_seconds())

    # generate url
    if market == "tw":
        market = "tw_stock_news"
    elif market == "us":
        market = "us_stock"
    url = """https://api.cnyes.com/media/api/v1/newslist/category/{market}?startAt={start}&endAt={end}&limit=30&page=1""".format(
        market=market, start=todayStartSec, end=todayEndSec)

    # generate header
    headers = {
        'User-Agent': """Mozilla/5.0
                    (Macintosh; Intel Mac OS X 10_10_1)
                    AppleWebKit/537.36 (KHTML, like Gecko)
                    Chrome/39.0.2171.95 Safari/537.36""",
        'Content-Type': 'application/json'
    }

    # get meta data form CNYES json response
    result = requests.get(url, headers, timeout=(2, 15))
    result.encoding = 'utf-8'
    jsdata = json.loads(result.text)

    # iterate all json pages
    dataCount = 0
    data = []
    lastPage = jsdata['items']['last_page']
    for page in range(lastPage):
        # get real all news from CNYES json response
        url = url.split("page=")[0] + "page=" + str(page+1)
        result = requests.get(url, headers, timeout=(2, 15))
        jsdata = json.loads(result.text)

        # iterate all news
        length = int(jsdata['items']['to']) - int(jsdata['items']['from']) + 1
        for index in range(length):
            element = jsdata['items']['data'][index]
            newsid = element['newsId']
            title = element['title']
            releaseTime = element['publishAt']
            releaseTime = epochTime + timedelta(seconds=releaseTime)
            newsUrl = "https://news.cnyes.com/news/id/{id}".format(id=newsid)

            stock_id = []
            # append 'code' to stock_id if tag 'market' exist
            if 'market' in element:
                for i in range(len(element['market'])):
                    # check if it is tw stock
                    if 'TWS' in element['market'][i]['symbol']:
                        stock_id.append(element['market'][i]['code'])
            # check stock_id not empty
            if len(stock_id) != 0:
                dataCount += 1

                tmp = {}
                tmp['link'] = newsUrl
                tmp['stock_id'] = stock_id
                tmp['title'] = title
                tmp['source'] = 'cnyes'
                tmp['releaseTime'] = releaseTime.isoformat()
                data.append(tmp)

    res = {}
    res["data_count"] = str(dataCount)
    res["data"] = data
    return res


if __name__ == '__main__':
    data = crawlNewsCnyes(market="tw")
    print(formatJSON(data))
