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

# ---------- выбор типа полиса ----------
def policy_type_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text=messages["policy_button_visa_d"][lang],
                callback_data="policy_visa_d"
            ),
            InlineKeyboardButton(
                text=messages["policy_button_trp"][lang],
                callback_data="policy_trp"
            ),
        ]]
    )
# ---------- выбор срока действия ----------
def term_keyboard(lang: str, policy_type: str) -> InlineKeyboardMarkup:
    """
    policy_type:
        visa_d   – только 90 дней
        trp      – 1 год / 13 месяцев / 2 года
    """
    if policy_type == "visa_d":
        terms = {
            "uk": [("90 днів",   "term_90d")],
            "en": [("90 days",   "term_90d")],
            "ru": [("90 дней",   "term_90d")]
        }
    else:  # trp
        terms = {
            "uk": [("1 рік",      "term_1y"),
                   ("13 місяців", "term_13m"),
                   ("2 роки",     "term_2y")],
            "en": [("1 year",     "term_1y"),
                   ("13 months",  "term_13m"),
                   ("2 years",    "term_2y")],
            "ru": [("1 год",      "term_1y"),
                   ("13 месяцев", "term_13m"),
                   ("2 года",     "term_2y")]
        }

    buttons = [
        InlineKeyboardButton(text=t, callback_data=cb)
        for t, cb in terms[lang]
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])
  
def citizenship_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура для выбора гражданства."""
    citizenships = {
        "uk": [("Україна", "ukraine"), ("Інше", "other")],
        "en": [("Ukraine", "ukraine"), ("Other", "other")],
        "ru": [("Украина", "ukraine"), ("Другое", "other")]
    }
    buttons = [InlineKeyboardButton(text=text, callback_data=f"citizenship_{data}") for text, data in citizenships[lang]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard

def consent_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура для согласия."""
    consent = {
        "uk": [("Так", "consent_yes"), ("Ні", "consent_no")],
        "en": [("Yes", "consent_yes"), ("No", "consent_no")],
        "ru": [("Да", "consent_yes"), ("Нет", "consent_no")]
    }
    buttons = [InlineKeyboardButton(text=text, callback_data=data) for text, data in consent[lang]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard

def price_confirmation_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения цены."""
    confirmation = {
        "uk": [("Так", "price_confirm_yes"), ("Ні", "price_confirm_no")],
        "en": [("Yes", "price_confirm_yes"), ("No", "price_confirm_no")],
        "ru": [("Да", "price_confirm_yes"), ("Нет", "price_confirm_no")]
    }
    buttons = [InlineKeyboardButton(text=text, callback_data=data) for text, data in confirmation[lang]]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard

def data_confirmation_keyboard(lang: str) -> InlineKeyboardMarkup:
    confirmation = {
        "uk": [("Так", "data_confirm_yes"), ("Ні", "data_confirm_no")],
        "en": [("Yes", "data_confirm_yes"), ("No", "data_confirm_no")],
        "ru": [("Да", "data_confirm_yes"), ("Нет", "data_confirm_no")]
    }
    buttons = [
        InlineKeyboardButton(text=txt, callback_data=cb)
        for txt, cb in confirmation[lang]
    ]
    return InlineKeyboardMarkup(inline_keyboard=[buttons])

def error_fields_keyboard(fields: list, lang: str) -> InlineKeyboardMarkup:
    """Клавиатура для выбора поля для исправления."""
    field_labels = {
        "birth_date": {
            "uk": "Дата народження",
            "en": "Birth date",
            "ru": "Дата рождения"
        },
        "full_name": {
            "uk": "ПІБ",
            "en": "Full name",
            "ru": "Полное имя"
        },
        "passport": {
            "uk": "Номер паспорта",
            "en": "Passport number",
            "ru": "Номер паспорта"
        },
        "phone": {
            "uk": "Телефон",
            "en": "Phone",
            "ru": "Телефон"
        },
        "email": {
            "uk": "Email",
            "en": "Email",
            "ru": "Email"
        },
            "gender": {
            "uk": "Стать",
            "en": "Gender",
            "ru": "Пол"
        },
        "citizenship": {
            "uk": "Громадянство",
            "en": "Citizenship",
            "ru": "Гражданство"
        },
        "address": {
            "uk": "Адреса",
            "en": "Address",
            "ru": "Адрес"
            },    
    }
    buttons = [InlineKeyboardButton(text=field_labels[field][lang], callback_data=f"edit_{field}") for field in fields]
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard

def gender_keyboard(lang: str):
    """
    Клавиатура с двумя кнопками:
    Жіноча / Чоловіча   (Female / Male)
    callback_data: gender_female  |  gender_male
    """
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=messages["gender_female"][lang],
            callback_data="gender_female"
        ),
        InlineKeyboardButton(
            text=messages["gender_male"][lang],
            callback_data="gender_male"
        )
    ]])