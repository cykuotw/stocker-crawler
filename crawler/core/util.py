import json

def formatJSON(json_data):
    """
    @Description:
        將JSON轉為適合印出來的格式
        Format json data prettier for printing in console
    @Param:
        json_data (json or dict)
    @Return:
        string
    """

    json_str = json.dumps(json_data, indent=2, ensure_ascii=False).encode('utf-8')
    return json_str.decode()