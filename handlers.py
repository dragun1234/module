# handlers.py
from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import bot
from keyboards import (
    language_keyboard,
    policy_type_keyboard,
    term_keyboard,
    gender_keyboard,
    consent_keyboard,
    price_confirmation_keyboard,
    data_confirmation_keyboard,
    error_fields_keyboard,
    messenger_keyboard
)
from localization import messages, field_names
from validators import (
    validate_date,
    calculate_age,
    validate_full_name,
    validate_passport,
    validate_phone,
    validate_address,
    validate_email
)
from utils import send_email, send_channel_message
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
import html
from logger import log_user_input, log_error, log_entry

term_map = {
    "90d":       {"uk": "90 днів",      "en": "90 days",      "ru": "90 дней"},
    "1_month":   {"uk": "1 місяць",     "en": "1 month",      "ru": "1 месяц"},
    "6_months":  {"uk": "6 місяців",    "en": "6 months",     "ru": "6 месяцев"},
    "1_year":    {"uk": "1 рік",        "en": "1 year",       "ru": "1 год"},
    "13_months": {"uk": "13 місяців",   "en": "13 months",    "ru": "13 месяцев"},
    "2_years":   {"uk": "2 роки",       "en": "2 years",      "ru": "2 года"}
}
router = Router()
class InsuranceForm(StatesGroup):
    language = State()
    consent_personal = State()  # Consent for personal data
    consent_contact = State()    # Consent for contact data
    policy_type = State()        # Type of insurance policy
    term = State()               # Term of the insurance
    citizenship = State()        # Citizenship of the user
    policy_start_date = State()  # Start date of the policy
    birth_date = State()         # User's birth date
    price_confirmation = State()  # Confirmation of the price
    last_name_trp = State()      # Last name for TRP
    first_name_trp = State()     # First name for TRP
    full_name = State()          # Full name of the user
    gender = State()             # Gender of the user
    passport = State()           # Passport information
    phone = State()              # Phone number
    email = State()              # Email address
    address = State()            # User's address
    data_review = State()        # Review of the data entered
    correction = State()         # Correction of the data
    messenger = State()          # Preferred messenger
@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    utm_code = message.text.split(" ")[1] if len(message.text.split(" ")) > 1 else None
    if utm_code:
        user_id = message.from_user.id if message.from_user and message.from_user.id else "unknown"
        await state.update_data(utm_code=utm_code)
        # Логирование и уведомление администратора
        await send_channel_message(f"Новый вход с UTM: {html.escape(utm_code)}, user_id: {user_id}")
    # Приветственное сообщение на трёх языках
    await message.answer("Будь ласка, оберіть мову / Please choose your language / Пожалуйста, выберите язык", reply_markup=language_keyboard())
    await state.set_state(InsuranceForm.language)
@router.callback_query(lambda c: c.data.startswith("lang_"), InsuranceForm.language)
async def process_language(callback_query: types.CallbackQuery, state: FSMContext):
    lang = callback_query.data.split("_")[1] if callback_query.data else "ru"
    await state.update_data(lang=lang)
    # Краткие кнопки, подробности — в тексте
    policy_explain = {
        "uk": (
            "Оберіть тип страхового полісу:\n"
            "Visa D — для отримання візи D\n"
            "ВНЖ (TRP) — для посвідки на тимчасове проживання"
        ),
        "en": (
            "Choose the type of insurance policy:\n"
            "Visa D — for D visa\n"
            "TRP — for temporary residence permit"
        ),
        "ru": (
            "Выберите тип страхового полиса:\n"
            "Visa D — для визы D\n"
            "ВНЖ (TRP) — для вида на жительство"
        )
    }
    await bot.send_message(
        callback_query.from_user.id,
        policy_explain[lang],
        reply_markup=policy_type_keyboard(lang)
    )
    await state.set_state(InsuranceForm.policy_type)
@router.callback_query(lambda c: c.data.startswith("policy_"), InsuranceForm.policy_type)
async def process_policy(callback_query: types.CallbackQuery, state: FSMContext):
    full_tag = callback_query.data or "policy_visa_d"
    code = full_tag.split("_", 1)[1] if "_" in full_tag else "visa_d"
    await state.update_data(policy=code)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = messages["term_choice"][lang]
    await bot.send_message(
        callback_query.from_user.id,
        text,
        reply_markup=term_keyboard(lang, code)
    )
    await state.set_state(InsuranceForm.term)
@router.callback_query(lambda c: c.data.startswith("term_"), InsuranceForm.term)
async def process_term(callback_query: types.CallbackQuery, state: FSMContext):
    term = callback_query.data.split("_")[1] if callback_query.data else "1y"
    await state.update_data(term=term)
    data = await state.get_data()
    lang = data.get("lang", "ru")
    text = messages["citizenship_prompt"][lang]
    await bot.send_message(callback_query.from_user.id, text)
    await state.set_state(InsuranceForm.citizenship)
@router.message(InsuranceForm.citizenship)
async def process_citizenship(message: types.Message, state: FSMContext):
    try:
        log_user_input(message.from_user.id, 'citizenship', message.text.strip() if message.text else "")
    except Exception as e:
        log_error(message.from_user.id, 'citizenship', str(e))
    data = await state.get_data()
    lang = data.get("lang", "ru")
    await state.update_data(citizenship=message.text)
    await message.answer(messages["policy_start"][lang])
    await state.set_state(InsuranceForm.policy_start_date)
@router.message(InsuranceForm.policy_start_date)
async def process_policy_start(message: types.Message, state: FSMContext):
    try:
        log_user_input(message.from_user.id, 'policy_start_date', message.text.strip() if message.text else "")
    except Exception as e:
        log_error(message.from_user.id, 'policy_start_date', str(e))
    lang = (await state.get_data()).get("lang", "uk")
    date_str = message.text.strip() if message.text else ""
    from datetime import datetime, timedelta
    try:
        start_date = datetime.strptime(date_str, "%d.%m.%Y").date()
    except ValueError:
        await message.answer(messages["date_invalid"][lang])
        return
    today = datetime.today().date()
    if not (today < start_date <= today + timedelta(days=365*3)):
        await message.answer(messages["date_out_of_range"][lang])
        return
    await state.update_data(policy_start_date=date_str)
    await state.set_state(InsuranceForm.birth_date)
    await message.answer(messages["enter_birth_date"][lang])
    try:
        log_user_input(message.from_user.id, 'policy_start_date', message.text.strip() if message.text else "")
    except Exception as e:
        log_error(message.from_user.id, 'policy_start_date', str(e))
        raise

@router.callback_query(lambda c: c.data in ["consent_yes", "consent_no"], InsuranceForm.consent_contact)
async def process_consent_contact(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "consent_no":
        data = await state.get_data()
        lang = data.get("lang", "ru")
        await bot.send_message(callback_query.from_user.id, messages["operation_cancelled"][lang])
        await state.clear()
    else:
        data = await state.get_data()
        lang = data.get("lang", "ru")
        text = messages["policy_choice"][lang]
        await bot.send_message(
        callback_query.from_user.id,
        text,
        reply_markup=policy_type_keyboard(lang)
        )
        await state.set_state(InsuranceForm.policy_type)
@router.callback_query(lambda c: c.data in ["consent_yes", "consent_no"], InsuranceForm.consent_contact)
async def process_consent_contact(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "consent_no":
        data = await state.get_data()
        lang = data.get("lang", "ru")
        await bot.send_message(callback_query.from_user.id, messages["operation_cancelled"][lang])
        await state.clear()
    else:
        data = await state.get_data()
        lang = data.get("lang", "ru")
        text = messages["policy_choice"][lang]
        await bot.send_message(
        callback_query.from_user.id,
        text,
        reply_markup=policy_type_keyboard(lang)
        )
        await state.set_state(InsuranceForm.policy_type)
@router.message(InsuranceForm.birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    try:
        log_user_input(message.from_user.id, 'birth_date', message.text.strip() if message.text else "")
    except Exception as e:
        log_error(message.from_user.id, 'birth_date', str(e))
    data = await state.get_data()
    lang = data.get("lang", "ru")
    birth_date = validate_date(message.text or "")
    if not birth_date:
        await message.answer(messages["invalid_date"][lang])
        return
    age = calculate_age(birth_date)
    if age > 70:
        await message.answer(messages["age_error"][lang])
        await state.clear()
        return
    await state.update_data(birth_date=message.text, age=age)
    policy = data.get("policy")
    term    = data.get("term")
    if policy == "visa_d":
        price = 1000 if age <= 60 else 2000
    else:
        short_term = (
            "1_year"     if "1y"  in term else
            "13_months"  if "13m" in term else
            "2_years"    if "2y"  in term else
            None
        )
        if short_term is None:
            await message.answer(
                messages["term_choice"][lang]
            )
            await state.set_state(InsuranceForm.term)
            return
        if age <= 60:
            if short_term == "1_year":
                price = 1100
            elif short_term == "13_months":
                price = 1200
            elif short_term == "2_years":
                price = 2200
        else:
            if short_term == "1_year":
                price = 2000
            elif short_term == "13_months":
                price = 2300
            elif short_term == "2_years":
                price = 4000
    await state.update_data(price=price)
    text = messages["price_offer"][lang].format(price=price)
    await message.answer(text, reply_markup=price_confirmation_keyboard(lang))
    await state.set_state(InsuranceForm.price_confirmation)
@router.callback_query(lambda c: c.data in ["price_confirm_yes", "price_confirm_no"], InsuranceForm.price_confirmation)
async def process_price_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    policy = data.get("policy", "")
    price = data.get("price", "")
    utm_code = data.get("utm_code", "")

    if callback_query.data == "price_confirm_no":
        operation_cancelled = messages.get("operation_cancelled", {})
        if isinstance(operation_cancelled, dict) and lang in operation_cancelled:
            await bot.send_message(callback_query.from_user.id, operation_cancelled.get(lang, "Операция отменена."))
        await state.clear()
    else:
        # Логирование UTM и стоимости
        if utm_code and price:
            log_entry(utm_code, str(price))

        if policy == "trp":
            # Первый шаг: фамилия (укр/англ)
            prompt_msgs = {
                "uk": "Введіть прізвище українською та англійською, як вказано в перекладі паспорта. Приклад: Сміт (SMITH)",
                "en": "Enter your last name in Ukrainian and English as in the passport translation. Example: Сміт (SMITH)",
                "ru": "Введите фамилию на украинском и английском, как в переводе паспорта. Пример: Сміт (SMITH)"
            }
            await bot.send_message(callback_query.from_user.id, prompt_msgs.get(lang, "Введите фамилию."))
            await state.set_state(InsuranceForm.last_name_trp)
        else:
            enter_full_name = messages.get("enter_full_name", {})
            if isinstance(enter_full_name, dict) and lang in enter_full_name:
                await bot.send_message(callback_query.from_user.id, enter_full_name.get(lang, "Введите ваше ФИО."))
            await state.set_state(InsuranceForm.full_name)

# Для TRP: шаг 1 — фамилия
@router.message(InsuranceForm.last_name_trp)
async def process_last_name_trp(message: types.Message, state: FSMContext):
    try:
        log_user_input(message.from_user.id, 'last_name_trp', message.text.strip() if message.text else "")
    except Exception as e:
        log_error(message.from_user.id, 'last_name_trp', str(e))
    data = await state.get_data()
    lang = data.get("lang", "ru")
    last_name = message.text.strip() if message.text else ""
    # Проверка: только укр/англ буквы, пробелы, дефисы, скобки
    pattern = r"^[А-ЩЬЮЯҐЄІЇA-Z'\s\-()а-щьюяґєіїa-z]+$"
    if not re.match(pattern, last_name, re.IGNORECASE):
        error_msgs = {
            "uk": "Прізвище має містити лише українські та англійські літери, пробіли, дужки. Спробуйте ще раз.",
            "en": "Last name must contain only Ukrainian and English letters, spaces and brackets. Please try again.",
            "ru": "Фамилия должна содержать только украинские и английские буквы, пробелы, скобки. Попробуйте ещё раз."
        }
        await message.answer(error_msgs[lang])
        return
    await state.update_data(last_name_trp=last_name)
    # Переход к имени
    prompt_msgs = {
        "uk": "Введіть ім'я українською та англійською, як вказано в перекладі паспорта. Приклад: Джон (John)",
        "en": "Enter your first name in Ukrainian and English as in the passport translation. Example: Джон (John)",
        "ru": "Введите имя на украинском и английском, как в переводе паспорта. Пример: Джон (John)"
    }
    await message.answer(prompt_msgs[lang])
    await state.set_state(InsuranceForm.first_name_trp)

# Для TRP: шаг 2 — имя
@router.message(InsuranceForm.first_name_trp)
async def process_first_name_trp(message: types.Message, state: FSMContext):
    try:
        log_user_input(message.from_user.id, 'first_name_trp', message.text.strip() if message.text else "")
    except Exception as e:
        log_error(message.from_user.id, 'first_name_trp', str(e))
    data = await state.get_data()
    lang = data.get("lang", "ru")
    first_name = message.text.strip() if message.text else ""
    pattern = r"^[А-ЩЬЮЯҐЄІЇA-Z'\s\-()а-щьюяґєіїa-z]+$"
    if not re.match(pattern, first_name, re.IGNORECASE):
        error_msgs = {
            "uk": "Ім'я має містити лише українські та англійські літери, пробіли, дужки. Спробуйте ще раз.",
            "en": "First name must contain only Ukrainian and English letters, spaces and brackets. Please try again.",
            "ru": "Имя должно содержать только украинские и английские буквы, пробелы, скобки. Попробуйте ещё раз."
        }
        await message.answer(error_msgs[lang])
        return
    await state.update_data(first_name_trp=first_name)
    # Не сохраняем склеенное ФИО в full_name для TRP, используем только отдельные поля
    prompt_msgs = {
        "uk": "Виберіть Вашу стать:",
        "en": "Choose your gender:",
        "ru": "Выберите ваш пол:"
    }
    await message.answer(
        prompt_msgs[lang],
        reply_markup=gender_keyboard(lang)
    )
    await state.set_state(InsuranceForm.gender)

# Для остальных полисов — стандартный ввод ФИО
@router.message(InsuranceForm.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    try:
        log_user_input(message.from_user.id, 'full_name', message.text.strip() if message.text else "")
    except Exception as e:
        log_error(message.from_user.id, 'full_name', str(e))
    data = await state.get_data()
    lang = data.get("lang", "ru")
    full_name = message.text.strip() if message.text else ""
    if not validate_full_name(full_name):
        await message.answer(messages["invalid_full_name"][lang])
        return
    await state.update_data(full_name=full_name)
    await message.answer(
        messages["gender_prompt"][lang],
        reply_markup=gender_keyboard(lang)
    )
    await state.set_state(InsuranceForm.gender)
@router.callback_query(lambda c: c.data.startswith("gender_"), InsuranceForm.gender)
async def process_gender(callback_query: types.CallbackQuery, state: FSMContext):
    try:
        log_user_input(callback_query.from_user.id, 'gender', callback_query.data)
    except Exception as e:
        log_error(callback_query.from_user.id, 'gender', str(e))
    lang = (await state.get_data()).get("lang", "ru")
    gender = "female" if callback_query.data.endswith("female") else "male"
    await state.update_data(gender=gender)
    await bot.send_message(callback_query.from_user.id, messages["enter_passport"][lang])
    await state.set_state(InsuranceForm.passport)
    try:
        log_user_input(callback_query.from_user.id, 'gender', callback_query.data)
    except Exception as e:
        log_error(callback_query.from_user.id, 'gender', str(e))
        raise
@router.message(InsuranceForm.passport)
async def process_passport(message: types.Message, state: FSMContext):
    try:
        log_user_input(message.from_user.id, 'passport', message.text.strip() if message.text else "")
    except Exception as e:
        log_error(message.from_user.id, 'passport', str(e))
    data = await state.get_data()
    lang = data.get("lang", "ru")
    if not validate_passport(message.text or ""):
        await message.answer(messages["invalid_passport"][lang])
        return
    await state.update_data(passport=message.text)
    await message.answer(messages["enter_phone"][lang])
    await state.set_state(InsuranceForm.phone)
    try:
        log_user_input(message.from_user.id, 'passport', message.text.strip() if message.text else "")
    except Exception as e:
        log_error(message.from_user.id, 'passport', str(e))
        raise
@router.message(InsuranceForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    try:
        log_user_input(message.from_user.id, 'phone', message.text.strip() if message.text else "")
    except Exception as e:
        log_error(message.from_user.id, 'phone', str(e))
    data = await state.get_data()
    lang = data.get("lang", "ru")
    policy = data.get("policy")
    if policy == "trp":
        prompt_msgs = {
            "uk": (
                "Введіть номер українського мобільного телефону (Kyivstar, Vodafone, lifecell) у форматі +380XXXXXXXXX. Тільки 9 цифр після +380. Наприклад: +380931234567"
            ),
            "en": (
                "Enter your Ukrainian mobile phone number (Kyivstar, Vodafone, lifecell) in the format +380XXXXXXXXX. Only 9 digits after +380. Example: +380931234567"
            ),
            "ru": (
                "Введите номер украинского мобильного телефона (Kyivstar, Vodafone, lifecell) в формате +380XXXXXXXXX. Только 9 цифр после +380. Например: +380931234567"
            )
        }
        user_input = (message.text.strip() if message.text else "").replace(" ", "")
        if user_input.startswith('+'):
            user_input = '+' + re.sub(r'\D', '', user_input[1:])
        else:
            user_input = re.sub(r'\D', '', user_input)
            if user_input.startswith('380'):
                user_input = '+' + user_input
            elif user_input.startswith('0') and len(user_input) == 10:
                user_input = '+380' + user_input[1:]
            elif len(user_input) == 9:
                user_input = '+380' + user_input
        if not (user_input.startswith('+380') and len(user_input) == 13 and user_input[4:].isdigit()):
            await message.answer(prompt_msgs[lang])
            return
        digits = user_input[4:]
        allowed_codes = {"39", "67", "68", "96", "97", "98", "50", "66", "95", "99", "63", "73", "93"}
        if digits[:2] not in allowed_codes:
            code_error_msgs = {
                "uk": "Номер має починатися з коду мобільного оператора Kyivstar, Vodafone або lifecell.",
                "en": "The number must start with a Ukrainian mobile operator code: Kyivstar, Vodafone or lifecell.",
                "ru": "Номер должен начинаться с кода мобильного оператора: Kyivstar, Vodafone или lifecell."
            }
            await message.answer(code_error_msgs[lang])
            return
        phone = user_input
        await state.update_data(phone=phone)
        # После телефона спрашиваем мессенджер
        await message.answer(messages["choose_messenger"][lang], reply_markup=messenger_keyboard(lang))
        await state.set_state(InsuranceForm.messenger)
        return
    if not validate_phone(message.text or ""):
        await message.answer(messages["invalid_phone"][lang])
        return
    await state.update_data(phone=message.text)
    await message.answer(messages["choose_messenger"][lang], reply_markup=messenger_keyboard(lang))
    await state.set_state(InsuranceForm.messenger)
    try:
        log_user_input(message.from_user.id, 'phone', message.text.strip() if message.text else "")
    except Exception as e:
        log_error(message.from_user.id, 'phone', str(e))
        raise
@router.message(InsuranceForm.messenger)
async def process_messenger(message: types.Message, state: FSMContext):
    lang = (await state.get_data()).get("lang", "uk")
    text = message.text.strip().lower()
    # Приводим к стандартному виду
    if "viber" in text:
        value = "Viber"
    elif "whatsapp" in text:
        value = "WhatsApp"
    elif "telegram" in text:
        value = "Telegram"
    else:
        await message.answer(messages["choose_messenger"][lang], reply_markup=messenger_keyboard(lang))
        return
    await state.update_data(messenger=value)
    # Переходим к email
    await message.answer(messages["enter_email"][lang])
    await state.set_state(InsuranceForm.email)
@router.callback_query(lambda c: c.data.startswith("messenger_"), InsuranceForm.messenger)
async def process_messenger_callback(callback_query: types.CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get("lang", "uk")
    data_map = {
        "messenger_viber": "Viber",
        "messenger_whatsapp": "WhatsApp",
        "messenger_telegram": "Telegram"
    }
    value = data_map.get(callback_query.data)
    if not value:
        await callback_query.message.answer(messages["choose_messenger"][lang], reply_markup=messenger_keyboard(lang))
        return
    await state.update_data(messenger=value)
    await callback_query.message.answer(messages["enter_email"][lang])
    await state.set_state(InsuranceForm.email)
@router.message(InsuranceForm.email)
async def process_email(message: types.Message, state: FSMContext):
    try:
        log_user_input(message.from_user.id, 'email', message.text.strip() if message.text else "")
    except Exception as e:
        log_error(message.from_user.id, 'email', str(e))
    data = await state.get_data()
    lang = data.get("lang", "ru")
    if not validate_email(message.text or ""):
        await message.answer(messages["invalid_email"][lang])
        return
    await state.update_data(email=message.text)
    await message.answer(messages["enter_address"][lang])
    await state.set_state(InsuranceForm.address)
    try:
        log_user_input(message.from_user.id, 'email', message.text.strip() if message.text else "")
    except Exception as e:
        log_error(message.from_user.id, 'email', str(e))
        raise
@router.message(InsuranceForm.address)
async def process_address(message: types.Message, state: FSMContext):
    try:
        log_user_input(message.from_user.id, 'address', message.text.strip() if message.text else "")
        # Сохраняем адрес в state сразу после ввода
        await state.update_data(address=message.text.strip() if message.text else "")
    except Exception as e:
        user_id = message.from_user.id if message.from_user and hasattr(message.from_user, "id") else 0
        log_error(user_id, 'address', str(e))
    data = await state.get_data()
    lang = data.get("lang", "ru")
    labels = messages["field_labels"][lang]
    policy = data.get("policy")
    # Короткие подписи для полиса из messages
    if policy == "visa_d":
        policy_human = messages["policy_button_visa_d_short"][lang]
    elif policy == "trp":
        policy_human = messages["policy_button_trp_short"][lang]
    else:
        policy_human = policy
    term_code = data.get("term")
    term_human = term_map.get(term_code, {}).get(lang)
    if not term_human:
        if term_code and "2y" in term_code:
            term_human = term_map["2_years"][lang]
        elif term_code and "1y" in term_code:
            term_human = term_map["1_year"][lang]
        elif term_code and "13m" in term_code:
            term_human = term_map["13_months"][lang]
        elif term_code and "6m" in term_code:
            term_human = term_map["6_months"][lang]
        elif term_code and "1m" in term_code:
            term_human = term_map["1_month"][lang]
        elif term_code and "90d" in term_code:
            term_human = term_map["90d"][lang]
        else:
            term_human = term_code
    # Для TRP выводим имя и фамилию отдельными строками
    if data.get("policy") == "trp" and data.get("last_name_trp") and data.get("first_name_trp"):
        summary = (
            f"{labels.get('policy_type', 'Тип полиса')}: {html.escape(str(policy_human or ''))}\n"
            f"{labels.get('policy_term', 'Срок')}: {html.escape(str(term_human or ''))}\n"
            f"{labels.get('policy_start', 'Старт')}: {html.escape(str(data.get('policy_start_date', '')))}\n"
            f"{labels.get('policy_price', 'Цена')}: {html.escape(str(data.get('price', '')))} UAH\n"
            f"Прізвище: {html.escape(str(data.get('last_name_trp', '')))}\n"
            f"Ім'я: {html.escape(str(data.get('first_name_trp', '')))}\n"
            f"{html.escape(field_names[lang].get('birth_date', 'Дата рождения'))}: {html.escape(str(data.get('birth_date', '')))}\n"
            f"{html.escape(field_names[lang].get('passport', 'Паспорт'))}: {html.escape(str(data.get('passport', '')))}\n"
            f"{html.escape(field_names[lang].get('address', 'Адрес'))}: {html.escape(str(data.get('address', '')))}\n"
            f"{labels.get('gender', 'Пол')}: {html.escape(str(data.get('gender', '')))}\n"
            f"{labels.get('citizenship', 'Гражданство')}: {html.escape(str(data.get('citizenship', '')))}\n"
            f"{html.escape(field_names[lang].get('phone', 'Телефон'))}: {html.escape(str(data.get('phone', '')))}\n"
            f"{html.escape(field_names[lang].get('email', 'Email'))}: {html.escape(str(data.get('email', '')))}\n"
            f"{html.escape(field_names[lang].get('messenger', 'Мессенджер'))}: {html.escape(str(data.get('messenger', '')))}"
        )
    else:
        fio = data.get("full_name", "")
        summary = (
            f"{labels.get('policy_type', 'Тип полиса')}: {html.escape(str(policy_human or ''))}\n"
            f"{labels.get('policy_term', 'Срок')}: {html.escape(str(term_human or ''))}\n"
            f"{labels.get('policy_start', 'Старт')}: {html.escape(str(data.get('policy_start_date', '')))}\n"
            f"{labels.get('policy_price', 'Цена')}: {html.escape(str(data.get('price', '')))} UAH\n"
            f"{html.escape(field_names[lang].get('full_name', 'ФИО'))}: {html.escape(str(fio))}\n"
            f"{html.escape(field_names[lang].get('birth_date', 'Дата рождения'))}: {html.escape(str(data.get('birth_date', '')))}\n"
            f"{html.escape(field_names[lang].get('passport', 'Паспорт'))}: {html.escape(str(data.get('passport', '')))}\n"
            f"{html.escape(field_names[lang].get('address', 'Адрес'))}: {html.escape(str(data.get('address', '')))}\n"
            f"{labels.get('gender', 'Пол')}: {html.escape(str(data.get('gender', '')))}\n"
            f"{labels.get('citizenship', 'Гражданство')}: {html.escape(str(data.get('citizenship', '')))}\n"
            f"{html.escape(field_names[lang].get('phone', 'Телефон'))}: {html.escape(str(data.get('phone', '')))}\n"
            f"{html.escape(field_names[lang].get('email', 'Email'))}: {html.escape(str(data.get('email', '')))}\n"
            f"{html.escape(field_names[lang].get('messenger', 'Мессенджер'))}: {html.escape(str(data.get('messenger', '')))}"
        )
    await state.set_state(InsuranceForm.data_review)
    text = messages["data_review"][lang].format(data=summary)
    await message.answer(text, reply_markup=data_confirmation_keyboard(lang), parse_mode="HTML")
@router.callback_query(
    lambda c: c.data in ["data_confirm_yes", "data_confirm_no"],
    InsuranceForm.data_review
)
async def process_data_review(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    if callback_query.data == "data_confirm_no":
        fields = [
            "birth_date",
            "policy_start",
            "full_name",
            "passport",
            "address",
            "citizenship",
            "phone",
            "email",
        ]
        await bot.send_message(
            callback_query.from_user.id,
            messages["edit_choose_field"][lang],
            reply_markup=error_fields_keyboard(fields, lang)
        )
        return
    policy = data.get("policy")
    if policy == "visa_d":
        policy_human = messages["policy_button_visa_d_short"][lang]
    elif policy == "trp":
        policy_human = messages["policy_button_trp_short"][lang]
    else:
        policy_human = policy
    term_code = data.get("term")
    term_human = term_map.get(term_code, {}).get(lang)
    if not term_human and term_code:
        if "2y" in term_code:
            term_human = term_map["2_years"][lang]
        elif "1y" in term_code:
            term_human = term_map["1_year"][lang]
        elif "13m" in term_code:
            term_human = term_map["13_months"][lang]
        elif "6m" in term_code:
            term_human = term_map["6_months"][lang]
        elif "1m" in term_code:
            term_human = term_map["1_month"][lang]
        elif "90d" in term_code:
            term_human = term_map["90d"][lang]
    labels = messages["field_labels"][lang]
    # Для TRP выводим имя и фамилию отдельными строками
    if data.get("policy") == "trp" and data.get("last_name_trp") and data.get("first_name_trp"):
        summary = (
            f"{labels.get('policy_type', 'Тип полиса')}: {html.escape(str(policy_human or ''))}\n"
            f"{labels.get('policy_term', 'Срок')}: {html.escape(str(term_human or ''))}\n"
            f"{labels.get('policy_start', 'Старт')}: {html.escape(str(data.get('policy_start_date', '')))}\n"
            f"{labels.get('policy_price', 'Цена')}: {html.escape(str(data.get('price', '')))} UAH\n"
            f"Прізвище: {html.escape(str(data.get('last_name_trp', '')))}\n"
            f"Ім'я: {html.escape(str(data.get('first_name_trp', '')))}\n"
            f"{html.escape(field_names[lang].get('birth_date', 'Дата рождения'))}: {html.escape(str(data.get('birth_date', '')))}\n"
            f"{html.escape(field_names[lang].get('passport', 'Паспорт'))}: {html.escape(str(data.get('passport', '')))}\n"
            f"{html.escape(field_names[lang].get('address', 'Адрес'))}: {html.escape(str(data.get('address', '')))}\n"
            f"{labels.get('gender', 'Пол')}: {html.escape(str(data.get('gender', '')))}\n"
            f"{labels.get('citizenship', 'Гражданство')}: {html.escape(str(data.get('citizenship', '')))}\n"
            f"{html.escape(field_names[lang].get('phone', 'Телефон'))}: {html.escape(str(data.get('phone', '')))}\n"
            f"{html.escape(field_names[lang].get('email', 'Email'))}: {html.escape(str(data.get('email', '')))}\n"
            f"{html.escape(field_names[lang].get('messenger', 'Мессенджер'))}: {html.escape(str(data.get('messenger', '')))}"
        )
    else:
        fio = data.get("full_name", "")
        summary = (
            f"{labels.get('policy_type', 'Тип полиса')}: {html.escape(str(policy_human or ''))}\n"
            f"{labels.get('policy_term', 'Срок')}: {html.escape(str(term_human or ''))}\n"
            f"{labels.get('policy_start', 'Старт')}: {html.escape(str(data.get('policy_start_date', '')))}\n"
            f"{labels.get('policy_price', 'Цена')}: {html.escape(str(data.get('price', '')))} UAH\n"
            f"{html.escape(field_names[lang].get('full_name', 'ФИО'))}: {html.escape(str(fio))}\n"
            f"{html.escape(field_names[lang].get('birth_date', 'Дата рождения'))}: {html.escape(str(data.get('birth_date', '')))}\n"
            f"{html.escape(field_names[lang].get('passport', 'Паспорт'))}: {html.escape(str(data.get('passport', '')))}\n"
            f"{html.escape(field_names[lang].get('address', 'Адрес'))}: {html.escape(str(data.get('address', '')))}\n"
            f"{labels.get('gender', 'Пол')}: {html.escape(str(data.get('gender', '')))}\n"
            f"{labels.get('citizenship', 'Гражданство')}: {html.escape(str(data.get('citizenship', '')))}\n"
            f"{html.escape(field_names[lang].get('phone', 'Телефон'))}: {html.escape(str(data.get('phone', '')))}\n"
            f"{html.escape(field_names[lang].get('email', 'Email'))}: {html.escape(str(data.get('email', '')))}\n"
            f"{html.escape(field_names[lang].get('messenger', 'Мессенджер'))}: {html.escape(str(data.get('messenger', '')))}"
        )
    subject = "Новые данные для страхового полиса"
    await send_email(subject, summary, "igor@yrin.com")
    await send_channel_message(summary)
    await bot.send_message(callback_query.from_user.id, messages["data_sent"][lang])
    await state.clear()
@router.callback_query(lambda c: c.data.startswith("edit_"), InsuranceForm.data_review)
async def process_field_correction(callback_query: types.CallbackQuery, state: FSMContext):
    field = callback_query.data.split("edit_")[1]
    data = await state.get_data()
    lang = data.get("lang", "ru")
    policy = data.get("policy")
    prompt_map = {
        "birth_date": messages["enter_birth_date"][lang],
        "full_name": None,
        "passport": messages["enter_passport"][lang],
        "phone": messages["enter_phone"][lang],
        "email": messages["enter_email"][lang],
        "address": messages["enter_address"][lang],
        "gender": messages["gender_prompt"][lang],
        "citizenship": messages["citizenship_prompt"][lang],
        "term": messages["term_choice"][lang],
    }
    if field == "full_name" and policy == "trp":
        prompt_msgs = {
            "uk": "Введіть Ваше ПІБ українською та англійською. Приклад: Джон Сміт (John Smith)",
            "en": "Enter your full name in Ukrainian and English. Example: Джон Сміт (John Smith)",
            "ru": "Введите ваше ФИО на украинском и английском. Пример: Джон Смит (John Smith)"
        }
        prompt = prompt_msgs[lang]
    else:
        prompt = prompt_map.get(field, "Введите значение:")
    labels = messages["field_labels"][lang]
    field_label = field_names[lang].get(field) or labels.get(field) or field
    await bot.send_message(
        callback_query.from_user.id,
        messages["edit_enter_new"][lang].format(field=f"<b>{field_label}</b>") + f"\n{prompt}",
        parse_mode="HTML"
    )
    await state.update_data(field_to_edit=field)
    await state.set_state(InsuranceForm.correction)
@router.message(InsuranceForm.correction)
async def process_field_value(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    field = data.get("field_to_edit")
    try:
        log_user_input(message.from_user.id, field, message.text.strip())
    except Exception as e:
        log_error(message.from_user.id, field, str(e))
    policy = data.get("policy")
    value = message.text.strip()
    if not isinstance(field, str):
        await message.answer(messages["edit_choose_field"][lang])
        return
    if field == "full_name" and policy == "trp":
        pattern = r"^[а-щьюяґєіїa-zA-Z'\s\-()]+$"
        if not re.match(pattern, value, re.IGNORECASE):
            error_msgs = {
                "uk": "ПІБ має містити лише українські та англійські літери, пробіли та дужки. Спробуйте ще раз.",
                "en": "Full name must contain only Ukrainian and English letters, spaces and brackets. Please try again.",
                "ru": "Введите ваше ФИО на украинском и английском. Пример: Джон Смит (John Smith)"
            }
            await message.answer(error_msgs[lang])
            return
    await state.update_data(**{field: value})
    data = await state.get_data()
    labels = messages["field_labels"][lang]
    policy = data.get("policy")
    if policy == "visa_d":
        policy_human = messages["policy_button_visa_d_short"][lang]
    elif policy == "trp":
        policy_human = messages["policy_button_trp_short"][lang]
    else:
        policy_human = policy
    term_code = data.get("term")
    term_human = term_map.get(term_code, {}).get(lang)
    if not term_human and term_code:
        if "2y" in term_code:
            term_human = term_map["2_years"][lang]
        elif "1y" in term_code:
            term_human = term_map["1_year"][lang]
        elif "13m" in term_code:
            term_human = term_map["13_months"][lang]
        elif "6m" in term_code:
            term_human = term_map["6_months"][lang]
        elif "1m" in term_code:
            term_human = term_map["1_month"][lang]
        elif "90d" in term_code:
            term_human = term_map["90_days"][lang]
    # Для TRP выводим имя и фамилию отдельными строками
    if data.get("policy") == "trp" and data.get("last_name_trp") and data.get("first_name_trp"):
        summary = (
            f"{labels.get('policy_type', 'Тип полиса')}: {html.escape(str(policy_human or ''))}\n"
            f"{labels.get('policy_term', 'Срок')}: {html.escape(str(term_human or ''))}\n"
            f"{labels.get('policy_start', 'Старт')}: {html.escape(str(data.get('policy_start_date', '')))}\n"
            f"{labels.get('policy_price', 'Цена')}: {html.escape(str(data.get('price', '')))} UAH\n"
            f"Прізвище: {html.escape(str(data.get('last_name_trp', '')))}\n"
            f"Ім'я: {html.escape(str(data.get('first_name_trp', '')))}\n"
            f"{html.escape(field_names[lang].get('birth_date', 'Дата рождения'))}: {html.escape(str(data.get('birth_date', '')))}\n"
            f"{html.escape(field_names[lang].get('passport', 'Паспорт'))}: {html.escape(str(data.get('passport', '')))}\n"
            f"{html.escape(field_names[lang].get('address', 'Адрес'))}: {html.escape(str(data.get('address', '')))}\n"
            f"{labels.get('gender', 'Пол')}: {html.escape(str(data.get('gender', '')))}\n"
            f"{labels.get('citizenship', 'Гражданство')}: {html.escape(str(data.get('citizenship', '')))}\n"
            f"{html.escape(field_names[lang].get('phone', 'Телефон'))}: {html.escape(str(data.get('phone', '')))}\n"
            f"{html.escape(field_names[lang].get('email', 'Email'))}: {html.escape(str(data.get('email', '')))}\n"
            f"{html.escape(field_names[lang].get('messenger', 'Мессенджер'))}: {html.escape(str(data.get('messenger', '')))}\n"
        )
    else:
        fio = data.get("full_name", "")
        summary = (
            f"{labels.get('policy_type', 'Тип полиса')}: {html.escape(str(policy_human or ''))}\n"
            f"{labels.get('policy_term', 'Срок')}: {html.escape(str(term_human or ''))}\n"
            f"{labels.get('policy_start', 'Старт')}: {html.escape(str(data.get('policy_start_date', '')))}\n"
            f"{labels.get('policy_price', 'Цена')}: {html.escape(str(data.get('price', '')))} UAH\n"
            f"{html.escape(field_names[lang].get('full_name', 'ФИО'))}: {html.escape(str(fio))}\n"
            f"{html.escape(field_names[lang].get('birth_date', 'Дата рождения'))}: {html.escape(str(data.get('birth_date', '')))}\n"
            f"{html.escape(field_names[lang].get('passport', 'Паспорт'))}: {html.escape(str(data.get('passport', '')))}\n"
            f"{html.escape(field_names[lang].get('address', 'Адрес'))}: {html.escape(str(data.get('address', '')))}\n"
            f"{labels.get('gender', 'Пол')}: {html.escape(str(data.get('gender', '')))}\n"
            f"{labels.get('citizenship', 'Гражданство')}: {html.escape(str(data.get('citizenship', '')))}\n"
            f"{html.escape(field_names[lang].get('phone', 'Телефон'))}: {html.escape(str(data.get('phone', '')))}\n"
            f"{html.escape(field_names[lang].get('email', 'Email'))}: {html.escape(str(data.get('email', '')))}\n"
            f"{html.escape(field_names[lang].get('messenger', 'Мессенджер'))}: {html.escape(str(data.get('messenger', '')))}\n"
        )
    await state.set_state(InsuranceForm.data_review)
    text = messages["data_review"][lang].format(data=summary)
    await bot.send_message(
        message.chat.id,
        text,
        reply_markup=data_confirmation_keyboard(lang),
        parse_mode="HTML"
    )
    try:
        log_user_input(message.from_user.id, field, message.text.strip())
    except Exception as e:
        log_error(message.from_user.id, field, str(e))
        raise
def error_fields_keyboard(fields, lang):
    # Эта функция больше не возвращает клавиатуру выбора полиса, только для редактирования полей
    from keyboards import error_fields_keyboard as kbd_error_fields_keyboard
    return kbd_error_fields_keyboard(fields, lang)

