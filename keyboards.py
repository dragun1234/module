from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from localization import messages

def language_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора языка."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Українська", callback_data="lang_uk")],
        [InlineKeyboardButton(text="English", callback_data="lang_en")],
        [InlineKeyboardButton(text="Русский", callback_data="lang_ru")]
    ])
    return keyboard

def policy_type_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура для выбора типа полиса."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=messages["policy_choice"][lang], callback_data="policy_visa_d"),
            InlineKeyboardButton(text=messages["policy_choice"][lang], callback_data="policy_residence")
        ]
    ])
    return keyboard

def term_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура для выбора срока действия."""
    terms = {
        "🇺🇦 Українська": [("1 місяць", "1_month"), ("6 місяців", "6_months"), ("1 рік", "1_year")],
        "🇬🇧 English": [("1 month", "1_month"), ("6 months", "6_months"), ("1 year", "1_year")],
        "🇷🇺 Русский": [("1 месяц", "1_month"), ("6 месяцев", "6_months"), ("1 год", "1_year")]
    }
    buttons = [InlineKeyboardButton(text=text, callback_data=f"term_{data}") for text, data in terms[lang]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard

def citizenship_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура для выбора гражданства."""
    citizenships = {
        "🇺🇦 Українська": [("Україна", "ukraine"), ("Інше", "other")],
        "🇬🇧 English": [("Ukraine", "ukraine"), ("Other", "other")],
        "🇷🇺 Русский": [("Украина", "ukraine"), ("Другое", "other")]
    }
    buttons = [InlineKeyboardButton(text=text, callback_data=f"citizenship_{data}") for text, data in citizenships[lang]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard

def consent_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура для согласия."""
    consent = {
        "🇺🇦 Українська": [("Так", "consent_yes"), ("Ні", "consent_no")],
        "🇬🇧 English": [("Yes", "consent_yes"), ("No", "consent_no")],
        "🇷🇺 Русский": [("Да", "consent_yes"), ("Нет", "consent_no")]
    }
    buttons = [InlineKeyboardButton(text=text, callback_data=data) for text, data in consent[lang]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard

def price_confirmation_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения цены."""
    confirmation = {
        "🇺🇦 Українська": [("Так", "price_confirm_yes"), ("Ні", "price_confirm_no")],
        "🇬🇧 English": [("Yes", "price_confirm_yes"), ("No", "price_confirm_no")],
        "🇷🇺 Русский": [("Да", "price_confirm_yes"), ("Нет", "price_confirm_no")]
    }
    buttons = [InlineKeyboardButton(text=text, callback_data=data) for text, data in confirmation[lang]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard

def data_confirmation_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения данных."""
    confirmation = {
        "🇺🇦 Українська": [("Так", "data_confirm_yes"), ("Ні", "data_confirm_no")],
        "🇬🇧 English": [("Yes", "data_confirm_yes"), ("No", "data_confirm_no")],
        "🇷🇺 Русский": [("Да", "data_confirm_yes"), ("Нет", "data_confirm_no")]
    }
    buttons = [InlineKeyboardButton(text=text, callback_data=data) for text, data in confirmation[lang]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard

def error_fields_keyboard(fields: list, lang: str) -> InlineKeyboardMarkup:
    """Клавиатура для выбора поля для исправления."""
    field_labels = {
        "birth_date": {
            "🇺🇦 Українська": "Дата народження",
            "🇬🇧 English": "Birth date",
            "🇷🇺 Русский": "Дата рождения"
        },
        "full_name": {
            "🇺🇦 Українська": "ПІБ",
            "🇬🇧 English": "Full name",
            "🇷🇺 Русский": "Полное имя"
        },
        "passport": {
            "🇺🇦 Українська": "Номер паспорта",
            "🇬🇧 English": "Passport number",
            "🇷🇺 Русский": "Номер паспорта"
        },
        "phone": {
            "🇺🇦 Українська": "Телефон",
            "🇬🇧 English": "Phone",
            "🇷🇺 Русский": "Телефон"
        },
        "email": {
            "🇺🇦 Українська": "Email",
            "🇬🇧 English": "Email",
            "🇷🇺 Русский": "Email"
        },
        "address": {
            "🇺🇦 Українська": "Адреса",
            "🇬🇧 English": "Address",
            "🇷🇺 Русский": "Адрес"
        }
    }
    buttons = [InlineKeyboardButton(text=field_labels[field][lang], callback_data=f"edit_{field}") for field in fields]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard