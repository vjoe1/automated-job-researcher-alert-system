import pandas as pd
import constants as const


def extract_currency(text: str) -> str | pd.NA:
    if pd.isna(text) :
        return pd.NA

    code_match = const.CODE_PATTERN_LETTERS.search(text)
    if code_match:
        return code_match.group().upper()

    code_match = const.CODE_PATTERN_GLUED.search(text)
    if code_match:
        return code_match.group()

    symbol_match = const.SYMBOL_PATTERN.search(text)
    if symbol_match:
        return symbol_match.group()

    return pd.NA



def normalize_currency(code: str) -> str:
    if pd.isna(code):
        return pd.NA
    return const.SYMBOL_TO_CODE.get(code, code)



def format_number(num: float) -> str:
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M".replace('.0M', 'M')
    if num >= 1_000:
        return f"{num/1_000:.0f}K"
    return f"{num:.0f}"



def extract_salary_range(text: str , currency: str) -> str:
    if pd.isna(text) or pd.isna(currency) :
        return pd.NA

    salary_part = text.split('•')[0].strip()

    matches = const.NUMBER_PATTERN.findall(salary_part)
    if not matches:
        return pd.NA

    values = []
    for num_str, suffix in matches:
        num = float(num_str.replace(',', ''))
        num *= const.MULTIPLIERS.get(suffix, 1)
        values.append(num)
    if len(values) == 1:
        return f"{currency} {format_number(values[0])}"
    return f"{currency} {format_number(values[0])} - {format_number(values[1])}"



def extract_days_ago(text: str):
    if pd.isna(text):
        return pd.NA
    text = text.lower().strip()
    if text == 'today':
        return 0
    if text == 'yesterday':
        return 1
    match = const.POSTED_PATTERN.search(text)
    if not match:
        return pd.NA
    num = int(match.group(1)) if match.group(1) else 1
    unit = match.group(2)
    if unit == 'day':
        return num
    if unit == 'week':
        return num * 7
    if unit == 'month':
        return num * 30  
    if unit == 'year':
        return num * 365
    return pd.NA



def extract_salary_min_max(text: str):
    if pd.isna(text) :
        return pd.NA, pd.NA

    salary_part = text.split('•')[0].strip()

    matches = const.NUMBER_PATTERN.findall(salary_part)
    if not matches:
        return pd.NA, pd.NA

    values = []
    for num_str, suffix in matches:
        num = float(num_str.replace(',', ''))
        num *= const.MULTIPLIERS.get(suffix, 1)
        values.append(num)

    if len(values) == 1:
        return values[0], values[0]
    return values[0], values[-1]



def extract_employees(text: str):
    if pd.isna(text)  :
        return pd.NA, pd.NA

    match = const.EMPLOYEES_PATTERN.search(text)
    if not match:
        return pd.NA, pd.NA

    if match.group(1) and match.group(2):
        return int(match.group(1)), int(match.group(2))
    else:
        n = int(match.group(3))
        return n, pd.NA 



def extract_years(text: str):
    if pd.isna(text):
        return pd.NA, pd.NA

    match = const.YEARS_PATTERN.search(text)
    if not match:
        return pd.NA, pd.NA

    if match.group(1) and match.group(2):
        n1, n2 = int(match.group(1)), int(match.group(2))
        return min(n1, n2), max(n1, n2)
    else:
        n = int(match.group(3))
        return n, n