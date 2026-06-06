import json
import math
import os
import threading

from boto3 import client as boto3Client
from botocore.config import Config as botoConfig

from crawler.common.notifier import pushErrorMessage, pushNewsMessge


MAX_CONCURRENT_WORKERS = 7


def _error_result(totalSlice: int, currentSlice: int, errorType: str, message: str):
    return {
        "ok": False,
        "statusCode": 500,
        "currentSlice": currentSlice,
        "totalSlices": totalSlice,
        "stockCount": 0,
        "startIndex": None,
        "endIndex": None,
        "error": {
            "type": errorType,
            "message": message,
        },
    }


def _notify(message: str):
    print(message)
    try:
        pushNewsMessge(message)
    except Exception as ex:
        print(f"Yahoo crawler notification error: {type(ex).__name__}: {ex}")


def _notify_error(message: str, details=None):
    print(message)
    try:
        pushErrorMessage(message, crawler="yahoo-crawler", details=details)
    except Exception as ex:
        print(f"Yahoo crawler error notification error: {type(ex).__name__}: {ex}")


def _parse_payload(payload):
    if isinstance(payload, bytes):
        payload = payload.decode("utf-8")

    parsed = json.loads(payload)
    if isinstance(parsed, dict) and isinstance(parsed.get("body"), str):
        body = json.loads(parsed["body"])
        if isinstance(body, dict):
            return body

    return parsed


def _parse_invoke_response(invokeResponse, totalSlice: int, currentSlice: int):
    payload = invokeResponse["Payload"].read()

    try:
        parsedPayload = _parse_payload(payload)
    except Exception as ex:
        return _error_result(
            totalSlice,
            currentSlice,
            type(ex).__name__,
            f"Invalid worker payload: {ex}",
        )

    if invokeResponse.get("FunctionError"):
        return _error_result(
            totalSlice,
            currentSlice,
            "LambdaFunctionError",
            json.dumps(parsedPayload, ensure_ascii=False),
        )

    if not isinstance(parsedPayload, dict):
        return _error_result(
            totalSlice,
            currentSlice,
            "InvalidWorkerPayload",
            f"Expected object payload, got {type(parsedPayload).__name__}",
        )

    if parsedPayload.get("ok") is True and parsedPayload.get("statusCode") == 200:
        return parsedPayload

    error = parsedPayload.get("error")
    if not isinstance(error, dict):
        error = {
            "type": "WorkerError",
            "message": json.dumps(parsedPayload, ensure_ascii=False),
        }

    result = _error_result(
        totalSlice,
        currentSlice,
        str(error.get("type", "WorkerError")),
        str(error.get("message", "")),
    )
    result["currentSlice"] = parsedPayload.get("currentSlice", currentSlice)
    result["totalSlices"] = parsedPayload.get("totalSlices", totalSlice)
    return result


def task(totalSlice: int, currentSlice: int):
    msg = {
        "YAHOO_TOTAL_SLICE": f"{totalSlice}",
        "YAHOO_CURRENT_SLICE": f"{currentSlice}"
    }

    try:
        cfg = botoConfig(read_timeout=840, connect_timeout=600)
        lambdaClient = boto3Client('lambda', config=cfg)
        invokeResponse = lambdaClient.invoke(FunctionName="yahoo-crawler",
                                             InvocationType='RequestResponse',
                                             Payload=json.dumps(msg))
        result = _parse_invoke_response(invokeResponse, totalSlice, currentSlice)
    except Exception as ex:
        result = _error_result(
            totalSlice,
            currentSlice,
            type(ex).__name__,
            str(ex),
        )

    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return result


def _threadTask(totalSlice: int, currentSlice: int, results: list, lock):
    result = task(totalSlice, currentSlice)
    with lock:
        results.append(result)


def _summarize(totalSlice: int, results: list):
    results = sorted(results, key=lambda r: r.get("currentSlice") or 0)
    failed = [
        result
        for result in results
        if result.get("ok") is not True or result.get("statusCode") != 200
    ]
    failedSlices = [
        result.get("currentSlice")
        for result in failed
        if result.get("currentSlice") is not None
    ]
    errors = []
    for result in failed:
        error = result.get("error") or {}
        errors.append({
            "currentSlice": result.get("currentSlice"),
            "status": result.get("statusCode"),
            "type": error.get("type"),
            "message": error.get("message"),
        })

    successCount = len(results) - len(failed)
    return {
        "ok": len(failed) == 0,
        "statusCode": 200 if len(failed) == 0 else 500,
        "totalSlices": totalSlice,
        "successCount": successCount,
        "failedCount": len(failed),
        "failedSlices": failedSlices,
        "errors": errors,
        "results": results,
    }


def run(event, context):
    total = totalSlice = int(os.environ["YAHOO_TOTAL_SLICE"])
    results = []
    lock = threading.Lock()

    _notify(f"Yahoo crawler start. totalSlices={totalSlice}")

    chunkCnt = math.ceil(totalSlice/MAX_CONCURRENT_WORKERS)
    chunks = []
    for i in range(chunkCnt):
        curr = MAX_CONCURRENT_WORKERS
        if i == chunkCnt-1:
            curr = total
        chunks.append(curr)
        total -= MAX_CONCURRENT_WORKERS

    offset = 0
    for cnt in chunks:
        threads = []
        for i in range(cnt):
            currentSlice = i+1+offset
            t = threading.Thread(
                target=_threadTask,
                args=[totalSlice, currentSlice, results, lock],
            )
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        offset += cnt

    summary = _summarize(totalSlice, results)
    if summary["ok"]:
        _notify(f"Yahoo crawler done. success={summary['successCount']}/{totalSlice}")
    else:
        failedSlices = ",".join(str(s) for s in summary["failedSlices"])
        message = (
            "Yahoo crawler partial failed. "
            f"success={summary['successCount']}/{totalSlice} "
            f"failed={summary['failedCount']} "
            f"failedSlices={failedSlices}"
        )
        _notify_error(message, details=summary["errors"])

    return summary
