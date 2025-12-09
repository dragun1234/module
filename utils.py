import smtplib
from email.mime.text import MIMEText
from typing import Dict, Any

from config import EMAIL_ADDRESS, EMAIL_PASSWORD, CHANNEL_ID, bot
from localization import messages, field_names


async def send_email(subject: str, body: str, recipient: str) -> None:
    # Явно указываем кодировку UTF-8
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = str(EMAIL_ADDRESS or "")
    msg["To"] = recipient

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(str(EMAIL_ADDRESS or ""), str(EMAIL_PASSWORD or ""))
        server.sendmail(str(EMAIL_ADDRESS or ""), recipient, msg.as_string())
        server.quit()
    except Exception as e:
        print("Ошибка при отправке email:", e)


async def send_channel_message(text: str) -> None:
    # Отправляем только plain text, без parse_mode
    try:
        await bot.send_message(CHANNEL_ID, text, parse_mode=None)
    except Exception as e:
        print("Ошибка при отправке сообщения в канал:", e)





def _human_term(term_code: str, lang: str) -> str:
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
    Только plain text, без спецсимволов, эмодзи, HTML и Markdown.
    Переносы строк — только \n.
    """
    lang = data.get("lang", "uk")
    labels = messages["field_labels"][lang]
    policy_code = data.get("policy")
    if policy_code == "visa_d":
        policy_text = messages["policy_button_visa_d"][lang]
    elif policy_code == "trp":
        policy_text = messages["policy_button_trp"][lang]
    else:
        policy_text = str(policy_code)
    term_text = _human_term(data.get("term"), lang)
    # Формируем только обычный текст, без спецсимволов
    return (
        f"{labels['policy_type']}: {policy_text}\n"
        f"{labels['policy_term']}: {term_text}\n"
        f"{labels['policy_start']}: {data.get('policy_start_date', '—')}\n"
        f"{labels['policy_price']}: {data.get('price', '—')} UAH\n"
        f"{field_names[lang]['full_name']}: {data.get('full_name', '—')}\n"
        f"{field_names[lang]['birth_date']}: {data.get('birth_date', '—')}\n"
        f"{field_names[lang]['passport']}: {data.get('passport', '—')}\n"
        f"{field_names[lang]['address']}: {data.get('address', '—')}\n"
        f"{field_names[lang]['messenger']}: {data.get('messenger', '—')}\n"
        f"{labels['gender']}: {data.get('gender', '—')}\n"
        f"{labels['citizenship']}: {data.get('citizenship', '—')}\n"
        f"{field_names[lang]['phone']}: {data.get('phone', '—')}\n"
        f"{field_names[lang]['email']}: {data.get('email', '—')}"
    )
