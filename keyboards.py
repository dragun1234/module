# keyboards.py
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from localization import messages

def language_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Українська", callback_data="lang_uk")],
        [InlineKeyboardButton(text="English", callback_data="lang_en")],
        [InlineKeyboardButton(text="Русский", callback_data="lang_ru")]
    ])
    return keyboard

def policy_type_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[
            InlineKeyboardButton(
                text=messages["policy_button_visa_d_short"][lang],
                callback_data="policy_visa_d"
            ),
            InlineKeyboardButton(
                text=messages["policy_button_trp_short"][lang],
                callback_data="policy_trp"
            ),
        ]]
    )

def term_keyboard(lang: str, policy_type: str) -> InlineKeyboardMarkup:
    if policy_type == "visa_d":
        terms = {
            "uk": [("90 днів",   "term_90d")],
            "en": [("90 days",   "term_90d")],
            "ru": [("90 дней",   "term_90d")]
        }
    else:
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
    buttons = [InlineKeyboardButton(text=label, callback_data=code) for label, code in terms[lang]]
    return InlineKeyboardMarkup(inline_keyboard=[[b] for b in buttons])

def gender_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=messages["gender_male"][lang], callback_data="gender_male")],
            [InlineKeyboardButton(text=messages["gender_female"][lang], callback_data="gender_female")]
        ]
    )

def consent_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=messages["consent_yes"][lang], callback_data="consent_yes")],
            [InlineKeyboardButton(text=messages["consent_no"][lang], callback_data="consent_no")]
        ]
    )

def price_confirmation_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=messages["price_confirm_yes"][lang], callback_data="price_confirm_yes")],
            [InlineKeyboardButton(text=messages["price_confirm_no"][lang], callback_data="price_confirm_no")]
        ]
    )

def data_confirmation_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=messages["data_confirm_yes"][lang], callback_data="data_confirm_yes")],
            [InlineKeyboardButton(text=messages["data_confirm_no"][lang], callback_data="data_confirm_no")]
        ]
    )

def error_fields_keyboard(fields, lang):
    field_emojis = {
        "birth_date": "📅",
        "policy_start": "🗓️",
        "full_name": "👤",
        "passport": "🛄",
        "address": "🏠",
        "gender": "⚧️",
        "citizenship": "🌎",
        "phone": "📞",
        "email": "✉️",
        "term": "⏳",
    }
    short_labels = {
        "birth_date": {"uk": "Нар.", "en": "Birth", "ru": "Рожд."},
        "policy_start": {"uk": "Старт", "en": "Start", "ru": "Старт"},
        "full_name": {"uk": "ПІБ", "en": "Name", "ru": "ФИО"},
        "passport": {"uk": "Пасп.", "en": "Passp.", "ru": "Пасп."},
        "address": {"uk": "Адреса", "en": "Addr.", "ru": "Адрес"},
        "citizenship": {"uk": "Гром.", "en": "Citiz.", "ru": "Гражд."},
        "phone": {"uk": "Тел.", "en": "Phone", "ru": "Тел."},
        "email": {"uk": "Email", "en": "Email", "ru": "Email"},
        "term": {"uk": "Строк", "en": "Term", "ru": "Срок"},
    }
    buttons = []
    for field in fields:
        emoji = field_emojis.get(field, "")
        label = short_labels.get(field, {}).get(lang, field)
        text = f"{emoji} {label}".strip()
        buttons.append(InlineKeyboardButton(text=text, callback_data=f"edit_{field}"))
    keyboard = []
    for i in range(0, len(buttons), 2):
        keyboard.append(buttons[i:i+2])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def messenger_keyboard(lang: str):
    from localization import messages
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=messages["messenger_viber"][lang], callback_data="messenger_viber")],
            [InlineKeyboardButton(text=messages["messenger_whatsapp"][lang], callback_data="messenger_whatsapp")],
            [InlineKeyboardButton(text=messages["messenger_telegram"][lang], callback_data="messenger_telegram")],
        ]
    )