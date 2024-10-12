import json
import math
import os
import threading

from boto3 import client as boto3Client
from botocore.config import Config as botoConfig


def task(totalSlice: int, currentSlice: int):
    msg = {
        "YAHOO_TOTAL_SLICE": f"{totalSlice}",
        "YAHOO_CURRENT_SLICE": f"{currentSlice}"
    }
    cfg = botoConfig(read_timeout=840, connect_timeout=600)
    lambdaClient = boto3Client('lambda', config=cfg)

    invokeResponse = lambdaClient.invoke(FunctionName="yahoo-crawler",
                                         InvocationType='RequestResponse',
                                         Payload=json.dumps(msg))

    rspStr = invokeResponse['Payload'].read()
    rsp = json.loads(rspStr)
    print(rsp)


def run(event, context):
    RESERVED_CNT = 10

    total = totalSlice = int(os.environ["YAHOO_TOTAL_SLICE"])

    chunkCnt = math.ceil(totalSlice/RESERVED_CNT)
    chunks = []
    for i in range(chunkCnt):
        curr = RESERVED_CNT
        if i == chunkCnt-1:
            curr = total
        chunks.append(curr)
        total -= RESERVED_CNT

    offset = 0
    for cnt in chunks:
        threads = []
        for i in range(cnt):
            t = threading.Thread(target=task, args=[totalSlice, i+1+offset])
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        offset += cnt
