#!/bin/bash
cd ~/project/stocker-crawler
source venv/bin/activate
python3 -c 'from crawler.interface.derivatives import updateDailyVolatility; updateDailyVolatility()'
deactivate
exit 0
