#!/bin/bash
cd /home/ec2-user/project/stockerCrawler
source venv/bin/activate
python3 criticalInfoNotifier.py
deactivate
exit 0
