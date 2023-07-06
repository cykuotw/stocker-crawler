#!/bin/bash
cd $(dirname "$0")
source venv/bin/activate
python3 dailyRoutine.py
deactivate
exit 0
