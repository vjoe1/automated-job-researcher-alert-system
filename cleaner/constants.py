import re
from pathlib import Path



BASE_DIR = Path(__file__).resolve().parent.parent

SOURCE_DB_PATH = BASE_DIR / "scraper" / "scraped_jobs.db"
OUTPUT_DB_PATH = BASE_DIR / "backend" / "database" / "jobs.db"


SYMBOL_TO_CODE = {
    '$': 'USD', '€': 'EUR', '£': 'GBP', '¥': 'JPY',
    '₹': 'INR', '₩': 'KRW', '₺': 'TRY', '₽': 'RUB',
    '₴': 'UAH', '₦': 'NGN', '₱': 'PHP', '฿': 'THB',
    '₫': 'VND', '₪': 'ILS' , 'zł': 'PLN' , 'kr' : 'SEK'
}

MULTIPLIERS = {
    'k': 1_000, 'K': 1_000,
    'l': 100_000, 'L': 100_000,  
    'm': 1_000_000, 'M': 1_000_000,
    'cr': 10_000_000, 'CR': 10_000_000, 'Cr': 10_000_000,

}

YEARS_PATTERN = re.compile(r'(\d+)\s*-\s*(\d+)|(\d+)')
EMPLOYEES_PATTERN = re.compile(r'(\d+)\s*-\s*(\d+)|(\d+)\+')
POSTED_PATTERN = re.compile(r'(\d+)?\s*(day|week|month|year)s?\s*ago|today|yesterday')

NUMBER_PATTERN = re.compile(r'([\d,]+\.?\d*)\s*(cr|CR|Cr|[kKlLmM]?)')
CODE_PATTERN_LETTERS = re.compile(
    r'\b(USD|EUR|GBP|CAD|CHF|AUD|NZD|SGD|HKD|MXN|BRL|ZAR|AED|SAR)\b',
    re.IGNORECASE
)
CODE_PATTERN_GLUED = re.compile(
    r'\b(zł|kr)(?=\d|\s|$)',
    re.IGNORECASE
)
SYMBOL_PATTERN = re.compile(r'[\$€£¥₹₩₺₽₴₦₱฿₫₪]')
