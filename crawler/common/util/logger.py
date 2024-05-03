import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

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
