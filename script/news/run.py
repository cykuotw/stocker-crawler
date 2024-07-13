from crawler.news.cnyes import updateDailyNewsCnyes
from crawler.news.ctee import updateDailyNewsCtee
from crawler.news.udn import updateDailyNewsUdn


def run(event, context):
    """
    Runner function
    """
    updateDailyNewsCnyes()
    updateDailyNewsCtee()
    updateDailyNewsUdn()
