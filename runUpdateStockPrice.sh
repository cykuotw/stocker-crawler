#!/bin/bash
cd /home/ec2-user/project/stocker-crawler
source venv/bin/activate
python3 -c 'from crawler.interface.general import updateDailyPrice; updateDailyPrice()'
deactivate
exit 0
