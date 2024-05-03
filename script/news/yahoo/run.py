from crawler.news.yahoo import updateDailyNewsYahoo


def run(event, context):
    """
    Runner function
    """
    updateDailyNewsYahoo()
