from crawler.interface.priceBookRatio import handleDailyPeRatioAnalysis
from notifier.utils import pushSlackMessage
from datetime import datetime


if __name__ == '__main__':
    try:
        #date_time = datetime.strptime('2022-12-02', '%Y-%m-%d')
        date_time = datetime.now()
        handleDailyPeRatioAnalysis(date_time)
    except Exception as ex:
        print(ex)
        pushSlackMessage('Stocker淨值更新', ex)

