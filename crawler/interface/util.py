import json
import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

##################
##   Settings   ##
##################

with open('settings/critical_file/server_config.json') as configReader:
    serverConf = json.loads(configReader.read())
stockerUrl = "http://{}:{}/api/v0".format(serverConf['ip'], serverConf['port'])

with open('settings/data_key_select/income_sheet_key_select.txt',
        encoding='utf-8') as income_sheet_key_select:
    incomeSheetKeySel = set(line.strip() for line in income_sheet_key_select)

SLEEP_TIME = 11

companyTypes = ['sii', 'otc', 'rotc', 'pub']

# logging setting
log_filename = datetime.now().strftime("log/crawler %Y-%m-%d.log")
if os.path.exists("log") is not True:
    os.mkdir("log")
fileHandler = TimedRotatingFileHandler(
    log_filename, when='D', interval=1,
    backupCount=30, encoding='UTF-8', delay=False, utc=False)
logger = logging.getLogger()
BASIC_FORMAT = '%(asctime)s %(levelname)- 8s in %(module)s: %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
fileHandler.setFormatter(formatter)
logger.addHandler(fileHandler)

###########################
##   Utility Functions   ##
###########################

def transformHeaderNoun(data, fileName):
    """this method is used to transefer header noun.

    Use receive fileName to get noun_conversion file,
    and use direction going to decide to replace the columns or index.

    Args:
        data: dataframe from crawler.
        file: a string of noun_conversion file.

    Return:
        dataframe

    Raises:
        Exception: An error occurred.
    """
    if data is None:
        return {}

    direction = {
        "basic_information": "columns",
        "month_revenue": "columns",
        "income_sheet": "index",
        "balance_sheet": "index",
        "cashflow": "index"
    }

    with open('noun_conversion/%s.json' % fileName,
             encoding='utf-8') as converFile:
        nounConvers = json.loads(converFile.read())

    if direction[fileName] == 'columns':
        headers = data.columns
    elif direction[fileName] == 'index':
        headers = data.index

    # 讀取noun_conversion時請記得使用 if key in dict 檢查是否需要替換key值
    new_headers = []
    for idx, header in enumerate(headers):
        if nounConvers.get(header) is not None:
            new_headers.append(nounConvers.get(header))
        else:
            new_headers.append(header)

    if direction[fileName] == 'columns':
        data.columns = new_headers
    elif direction[fileName] == 'index':
        data.index = new_headers

    return data
