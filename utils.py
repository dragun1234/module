import smtplib
from email.mime.text import MIMEText
from config import EMAIL_ADDRESS, EMAIL_PASSWORD, CHANNEL_ID, bot

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

async def send_channel_message(text: str):
    try:
        await bot.send_message(CHANNEL_ID, text)
    except Exception as e:
        print("Ошибка при отправке сообщения в канал:", e)

def format_insurance_data(data: dict) -> str:
    """
    Форматирует данные страхового полиса для отправки по email или в канал.
    """
    return (
        f"Дата рождения: {data.get('birth_date', 'Не указано')}\n"
        f"Полное имя: {data.get('full_name', 'Не указано')}\n"
        f"Номер паспорта: {data.get('passport', 'Не указано')}\n"
        f"Телефон: {data.get('phone', 'Не указано')}\n"
        f"Email: {data.get('email', 'Не указано')}\n"
        f"Адрес: {data.get('address', 'Не указано')}\n"
        f"Тип полиса: {data.get('policy', 'Не указано')}\n"
        f"Срок действия: {data.get('term', 'Не указано')}\n"
        f"Гражданство: {data.get('citizenship', 'Не указано')}\n"
        f"Стоимость: {data.get('price', 'Не указано')} грн"
    )