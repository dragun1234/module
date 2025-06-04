
import smtplib
from email.mime.text import MIMEText
from typing import Dict

from config import EMAIL_ADDRESS, EMAIL_PASSWORD, CHANNEL_ID, bot
from localization import messages, field_names


# ------------------  отправка email  ------------------
async def send_email(subject: str, body: str, recipient: str):
    msg = MIMEText(body, "plain")
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = recipient

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())
        server.quit()
    except Exception as e:
        print("Ошибка при отправке email:", e)


# ------------------  отправка в канал  ------------------
async def send_channel_message(text: str):
    try:
        await bot.send_message(CHANNEL_ID, text)
    except Exception as e:
        print("Ошибка при отправке сообщения в канал:", e)


# ------------------  форматирование данных  ------------------
def _human_policy(policy_code: str, lang: str) -> str:
    """Преобразовать visa_d → «Поліс для візи D» и т.д."""
    mapping: Dict[str, Dict[str, str]] = {
        "visa_d": {
            "uk": "Поліс для візи D",
            "en": "Insurance for visa D",
            "ru": "Полис для визы D",
        },
        "trp": {
            "uk": "Поліс для ВНЖ",
            "en": "Insurance for TRP",
            "ru": "Полис для ВНЖ",
        },
    }
    return mapping.get(policy_code, {}).get(lang, policy_code)


def _human_term(term_code: str, lang: str) -> str:
    """Преобразовать 90d / 1_year … в читаемый срок."""
    mapping: Dict[str, Dict[str, str]] = {
        "90d": {
            "uk": "90 днів",
            "en": "90 days",
            "ru": "90 дней",
        },
        "1_month": {
            "uk": "1 місяць",
            "en": "1 month",
            "ru": "1 месяц",
        },
        "6_months": {
            "uk": "6 місяців",
            "en": "6 months",
            "ru": "6 месяцев",
        },
        "1_year": {
            "uk": "1 рік",
            "en": "1 year",
            "ru": "1 год",
        },
        "13_months": {
            "uk": "13 місяців",
            "en": "13 months",
            "ru": "13 месяцев",
        },
        "2_years": {
            "uk": "2 роки",
            "en": "2 years",
            "ru": "2 года",
        },
    }
    return mapping.get(term_code, {}).get(lang, term_code)


def format_insurance_data(data: dict) -> str:
    """
    Формирует текст страхового полиса для email / канала
    в требуемом порядке и на нужном языке.
    """
    # язык сохранён в FSM при выборе
    lang = data.get("lang", "uk")

    labels = messages["field_labels"][lang]

    policy_text = _human_policy(data.get("policy"), lang)
    term_text = _human_term(data.get("term"), lang)

    return (
        f"{labels['policy_type']}: {policy_text}\n"
        f"{labels['policy_term']}: {term_text}\n"
        f"{labels['policy_start']}: {data.get('policy_start_date', '—')}\n"
        f"{labels['policy_price']}: {data.get('price', '—')} UAH\n"
        f"{field_names[lang]['full_name']}: {data.get('full_name', '—')}\n"
        f"{field_names[lang]['birth_date']}: {data.get('birth_date', '—')}\n"
        f"{field_names[lang]['passport']}: {data.get('passport', '—')}\n"
        f"{field_names[lang]['address']}: {data.get('address', '—')}\n"
        f"{labels['gender']}: {data.get('gender', '—')}\n"
        f"{labels['citizenship']}: {data.get('citizenship', '—')}\n"
        f"{field_names[lang]['phone']}: {data.get('phone', '—')}\n"
        f"{field_names[lang]['email']}: {data.get('email', '—')}"
    )
