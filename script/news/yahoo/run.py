import json
import os

from crawler.common.util.config import getYahooConfig
from crawler.news.yahoo import updateDailyNewsYahoo


def run(event, context):
    """
    Runner function
    """
    os.environ["YAHOO_CURRENT_SLICE"] = event["YAHOO_CURRENT_SLICE"]
    os.environ["YAHOO_TOTAL_SLICE"] = event["YAHOO_TOTAL_SLICE"]

    updateDailyNewsYahoo()
    config = getYahooConfig()

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps({
            "YAHOO_CURRENT_SLICE": config['current-slices'],
            "YAHOO_TOTAL_SLICE": config['total-slices'],
        })
    }
