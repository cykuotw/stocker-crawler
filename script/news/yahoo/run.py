import os

from crawler.news.yahoo import updateDailyNewsYahoo


def _slice_value(event, key):
    value = event.get(key)
    if value is None:
        value = os.environ.get(key)
    if value is None:
        return None
    return int(value)


def run(event, context):
    """
    Runner function
    """
    currentSlice = _slice_value(event, "YAHOO_CURRENT_SLICE")
    totalSlices = _slice_value(event, "YAHOO_TOTAL_SLICE")

    os.environ["YAHOO_CURRENT_SLICE"] = str(currentSlice)
    os.environ["YAHOO_TOTAL_SLICE"] = str(totalSlices)

    try:
        result = updateDailyNewsYahoo()

        return {
            "ok": True,
            "statusCode": 200,
            "currentSlice": result["currentSlice"],
            "totalSlices": result["totalSlices"],
            "stockCount": result["stockCount"],
            "startIndex": result["startIndex"],
            "endIndex": result["endIndex"],
            "error": None,
        }

    except Exception as ex:
        return {
            "ok": False,
            "statusCode": 500,
            "currentSlice": currentSlice,
            "totalSlices": totalSlices,
            "stockCount": 0,
            "startIndex": None,
            "endIndex": None,
            "error": {
                "type": type(ex).__name__,
                "message": str(ex),
            },
        }
