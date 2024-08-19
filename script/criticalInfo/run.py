from crawler.criticalInfo.criticalInfo import updateCriticalInfo


def run(event, context):
    """
    Runner function
    """
    updateCriticalInfo()
