#!/bin/bash
cd ~/project/stocker-crawler
# cd ~/stocker/stocker-crawler
source venv/bin/activate
python3 priceBookRatioUpdate.py
deactivate
exit 0
