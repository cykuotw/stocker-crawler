import json

from dotenv import load_dotenv

load_dotenv()


with open('configs/data_key_select/income_sheet_key_select.txt',
          encoding='utf-8') as income_sheet_key_select:
    incomeSheetKeySel = set(line.strip() for line in income_sheet_key_select)

with open('configs/data_key_select/balance_sheet_key_select.txt',
          encoding='utf-8') as balance_sheet_key_select:
    balanceSheetKeySel = set(line.strip() for line in balance_sheet_key_select)

with open('configs/data_key_select/cashflow_key_select.txt',
          encoding='utf-8') as cashflow_key_select:
    cashflowKeySel = set(line.strip() for line in cashflow_key_select)

companyTypes = ['sii', 'otc', 'rotc', 'pub']


def transformHeaderNoun(data, fileName):
    """
    @Description
        This method is used to transefer header noun.

        Use receive fileName to get noun_conversion file,
        and use direction going to decide to replace the columns or index.

    @Param:
        data => Dataframe from crawler.\n
        file => string (name of noun_conversion file)

    @Return:
        Dataframe (transferred data)

    @Raises:
        Exception: An error occurred.
    """
    if data is None:
        return {}

    direction = {
        "basic_information": "columns",
        "month_revenue": "columns",
        "income_sheet": "index",
        "balance_sheet": "index",
        "cashflow": "index"
    }

    with open(f"configs/noun_conversion/{fileName}.json",
              encoding='utf-8') as converFile:
        nounConvers = json.loads(converFile.read())

    if direction[fileName] == 'columns':
        headers = data.columns
    elif direction[fileName] == 'index':
        headers = data.index

    # 讀取noun_conversion時請記得使用 if key in dict 檢查是否需要替換key值
    newHeaders = []
    for _, header in enumerate(headers):
        if nounConvers.get(header) is not None:
            newHeaders.append(nounConvers.get(header))
        else:
            newHeaders.append(header)

    if direction[fileName] == 'columns':
        data.columns = newHeaders
    elif direction[fileName] == 'index':
        data.index = newHeaders

    return data
