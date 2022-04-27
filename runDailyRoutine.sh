#!/bin/bash
# cd ~/project/stocker
cd ~/stocker/stocker-crawler
source venv/bin/activate
python3 dailyRoutine.py
deactivate
exit 0