# validators.py
import re
from datetime import datetime

def validate_date(date_str: str):
    try:
        birth_date = datetime.strptime(date_str, "%d.%m.%Y")
        return birth_date
    except ValueError:
        return None

def calculate_age(birth_date: datetime):
    today = datetime.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age

def validate_full_name(name: str):
    pattern = r'^[A-Za-z\s]+$'
    return bool(re.match(pattern, name))

def validate_passport(passport: str):
    pattern = r'^[A-Za-z0-9]+$'
    return bool(re.match(pattern, passport))

def validate_phone(phone: str):
    pattern = r'^\+\d{10,15}$'
    return bool(re.match(pattern, phone))

def validate_address(address: str):
    return len(address.strip()) > 0

def validate_email(email: str):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def validate_term(term: str):
    allowed_terms = ["1_month", "6_months", "1_year"]
    return term in allowed_terms

def validate_citizenship(citizenship: str):
    allowed_citizenships = ["ukraine", "other"]
    return citizenship in allowed_citizenships
