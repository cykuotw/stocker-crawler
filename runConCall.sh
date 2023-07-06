#!/bin/bash
cd $(dirname "$0")
source venv/bin/activate
python3 -c 'from crawler.interface.conferenceCall import updateConferenceCallInfo; updateConferenceCallInfo()'
deactivate
exit 0
