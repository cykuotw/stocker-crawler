#!/bin/bash
cd $(dirname "$0")
source venv/bin/activate
python3 -c 'from crawler.interface.general import updateDailyPrice; updateDailyPrice()'
deactivate
exit 0
