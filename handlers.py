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
    error_fields_keyboard
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
import re
# ---------------- МАППИНГИ ДЛЯ ЧЕЛОВЕКОЧИТАЕМЫХ ПОДПИСЕЙ ----------------
policy_map = {
    "visa_d": {"uk": "Поліс для візи D",
               "en": "Insurance for visa D",
               "ru": "Полис для визы D"},
    "trp":    {"uk": "Поліс для ВНЖ",
               "en": "Insurance for TRP",
               "ru": "Полис для ВНЖ"}
}

term_map = {
    "90d":       {"uk": "90 днів",      "en": "90 days",      "ru": "90 дней"},
    "1_month":   {"uk": "1 місяць",     "en": "1 month",      "ru": "1 месяц"},
    "6_months":  {"uk": "6 місяців",    "en": "6 months",     "ru": "6 месяцев"},
    "1_year":    {"uk": "1 рік",        "en": "1 year",       "ru": "1 год"},
    "13_months": {"uk": "13 місяців",   "en": "13 months",    "ru": "13 месяцев"},
    "2_years":   {"uk": "2 роки",       "en": "2 years",      "ru": "2 года"}
}
# ------------------------------------------------------------------------
router = Router()

class InsuranceForm(StatesGroup):
    language = State()   # Шаг 1: Выбор языка
    consent_personal = State()
    consent_contact = State()
    policy_type = State()  # Тип полиса
    term = State()  # Срок действия
    citizenship = State()  # Гражданство
    policy_start_date     = State()     # Дата начало срока
    birth_date = State()
    price_confirmation = State()
    full_name = State()
    gender = State()# Стать
    passport = State()
    phone = State()
    email = State()
    address = State()
    data_review = State()
    correction = State()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """Начало работы. Выбор языка."""
    await state.set_state(InsuranceForm.language)
    await message.answer(messages["start"]["uk"], reply_markup=language_keyboard())

@router.callback_query(lambda c: c.data.startswith("lang_"), InsuranceForm.language)
async def process_language(callback_query: types.CallbackQuery, state: FSMContext):
    lang = callback_query.data.split("_")[1]          # uk / en / ru
    await state.update_data(lang=lang)                # ←  сохраняем код
    text = messages["consent_personal"][lang]
    await bot.send_message(
        callback_query.from_user.id,
        text,
        reply_markup=consent_keyboard(lang)
    )
    await state.set_state(InsuranceForm.consent_personal)

@router.callback_query(lambda c: c.data.startswith("policy_"), InsuranceForm.policy_type)
async def process_policy(callback_query: types.CallbackQuery, state: FSMContext):
    full_tag = callback_query.data                 # policy_visa_d  /  policy_trp
    code = full_tag.split("_", 1)[1]               # visa_d        /  trp
    await state.update_data(policy=code)           # сохраняем КОРОТКИЙ код

    data = await state.get_data()
    lang = data.get("lang", "ru")

    text = messages["term_choice"][lang]
    await bot.send_message(
        callback_query.from_user.id,
        text,
        reply_markup=term_keyboard(lang, code)     # ←  два аргумента
    )
    await state.set_state(InsuranceForm.term)

@router.callback_query(lambda c: c.data.startswith("term_"), InsuranceForm.term)
async def process_term(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора срока действия."""
    term = callback_query.data.split("_")[1]
    await state.update_data(term=term)
    data = await state.get_data()
    lang = data.get("lang", "ru")  # Получение языка из состояния
    print(f"[DEBUG] Current lang in term: {lang}")  # Отладочный вывод
    text = messages["citizenship_prompt"][lang]
    await bot.send_message(callback_query.from_user.id, text)
    await state.set_state(InsuranceForm.citizenship)

@router.message(InsuranceForm.citizenship)
async def process_citizenship(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "uk")
    text = message.text.strip()

    ALPH = {
        "uk": r"^[а-щьюяґєії'\s-]+$",
        "ru": r"^[а-яё'\s-]+$",
        "en": r"^[a-z'\s-]+$",
    }
    if not re.match(ALPH[lang], text, re.IGNORECASE):
        await message.answer(messages["citizenship_invalid"][lang])
        return

    await state.update_data(citizenship=text.title())
    await message.answer(messages["policy_start_prompt"][lang])
    await state.set_state(InsuranceForm.policy_start_date)

@router.message(InsuranceForm.policy_start_date)
async def process_policy_start(message: types.Message, state: FSMContext):
    lang = (await state.get_data()).get("lang", "uk")
    date_str = message.text.strip()

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


@router.callback_query(lambda c: c.data in ["consent_yes", "consent_no"], InsuranceForm.consent_personal)
async def process_consent_personal(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "consent_no":
        data = await state.get_data()
        lang = data.get("lang", "ru")
        await bot.send_message(callback_query.from_user.id, messages["operation_cancelled"][lang])
        await state.clear()
    else:
        data = await state.get_data()
        lang = data.get("lang", "ru")
        text = messages["consent_contact"][lang]
        await bot.send_message(callback_query.from_user.id, text, reply_markup=consent_keyboard(lang))
        await state.set_state(InsuranceForm.consent_contact)

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
    data = await state.get_data()
    lang = data.get("lang", "ru")
    birth_date = validate_date(message.text)
    if not birth_date:
        await message.answer(messages["invalid_date"][lang])
        return
    age = calculate_age(birth_date)
    if age > 70:
        await message.answer(messages["age_error"][lang])
        await state.clear()
        return
    
    await state.update_data(birth_date=message.text, age=age)
    policy = data.get("policy")      # visa_d / trp
    term    = data.get("term")       # 90d / 1_year / 13_months / 2_years

    # ------------------ прайс-лист ------------------
    if policy == "visa_d":
        # единственная цена зависит только от возраста
        price = 1000 if age <= 60 else 2000
    else:  # policy == "trp"
        # term приходит как term_1y / term_13m / term_2y
        # оставляем «ядро» для расчёта цены
        short_term = (
            "1_year"     if "1y"  in term else
            "13_months"  if "13m" in term else
            "2_years"    if "2y"  in term else
            None
        )

        # если срок не распознан – просим выбрать заново
        if short_term is None:
            await message.answer(
                messages["term_choice"][lang]  # тот же текст выбора срока
            )
            await state.set_state(InsuranceForm.term)
            return

        # ---- цены по возрасту ----
        if age <= 60:
            if short_term == "1_year":
                price = 1100
            elif short_term == "13_months":
                price = 1200
            elif short_term == "2_years":
                price = 2200
        else:  # 60–70 лет
            if short_term == "1_year":
                price = 2000
            elif short_term == "13_months":
                price = 2300
            elif short_term == "2_years":
                price = 4000

    # ------------------------------------------------
    await state.update_data(price=price)
    text = messages["price_offer"][lang].format(price=price)
    await message.answer(text, reply_markup=price_confirmation_keyboard(lang))
    await state.set_state(InsuranceForm.price_confirmation)

@router.callback_query(lambda c: c.data in ["price_confirm_yes", "price_confirm_no"], InsuranceForm.price_confirmation)
async def process_price_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    if callback_query.data == "price_confirm_no":
        await bot.send_message(callback_query.from_user.id, messages["operation_cancelled"][lang])
        await state.clear()
    else:
        await bot.send_message(callback_query.from_user.id, messages["enter_full_name"][lang])
        await state.set_state(InsuranceForm.full_name)

@router.message(InsuranceForm.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    if not validate_full_name(message.text):
        await message.answer(messages["invalid_full_name"][lang])
        return
    await state.update_data(full_name=message.text)
    await message.answer(
    messages["gender_prompt"][lang],
    reply_markup=gender_keyboard(lang)
)
    await state.set_state(InsuranceForm.gender)

@router.callback_query(lambda c: c.data.startswith("gender_"), InsuranceForm.gender)
async def process_gender(callback_query: types.CallbackQuery, state: FSMContext):
    lang = (await state.get_data()).get("lang", "ru")

    gender = "female" if callback_query.data.endswith("female") else "male"
    await state.update_data(gender=gender)

    await bot.send_message(callback_query.from_user.id, messages["enter_passport"][lang])
    await state.set_state(InsuranceForm.passport)

@router.message(InsuranceForm.passport)
async def process_passport(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    if not validate_passport(message.text):
        await message.answer(messages["invalid_passport"][lang])
        return
    await state.update_data(passport=message.text)
    await message.answer(messages["enter_phone"][lang])
    await state.set_state(InsuranceForm.phone)

@router.message(InsuranceForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    if not validate_phone(message.text):
        await message.answer(messages["invalid_phone"][lang])
        return
    await state.update_data(phone=message.text)
    await message.answer(messages["enter_email"][lang])
    await state.set_state(InsuranceForm.email)

@router.message(InsuranceForm.email)
async def process_email(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    if not validate_email(message.text):
        await message.answer(messages["invalid_email"][lang])
        return
    await state.update_data(email=message.text)
    await message.answer(messages["enter_address"][lang])
    await state.set_state(InsuranceForm.address)

@router.message(InsuranceForm.address)
async def process_address(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "ru")
    if not validate_address(message.text):
        await message.answer(messages["invalid_address"][lang])
        return
    await state.update_data(address=message.text)
    data = await state.get_data()

    labels = messages["field_labels"][lang]
    policy_human = policy_map.get(data.get("policy"), {}).get(lang, data.get("policy"))
    term_human   = term_map.get(data.get("term"), {}).get(lang, data.get("term"))
    summary = (
        f"{labels['policy_type']}: {policy_human}\n"
        f"{labels['policy_term']}: {term_human}\n"
        f"{labels['policy_start']}: {data.get('policy_start_date')}\n"
        f"{labels['policy_price']}: {data.get('price')} UAH\n"
        f"{field_names[lang]['full_name']}: {data.get('full_name')}\n"
        f"{field_names[lang]['birth_date']}: {data.get('birth_date')}\n"
        f"{field_names[lang]['passport']}: {data.get('passport')}\n"
        f"{field_names[lang]['address']}: {data.get('address')}\n"
        f"{labels['gender']}: {data.get('gender')}\n"
        f"{labels['citizenship']}: {data.get('citizenship')}\n"
        f"{field_names[lang]['phone']}: {data.get('phone')}\n"
        f"{field_names[lang]['email']}: {data.get('email')}\n"
    )
    await state.set_state(InsuranceForm.data_review)          # ← сперва фиксируем состояние
    text = messages["data_review"][lang].format(data=summary)
    await message.answer(text, reply_markup=data_confirmation_keyboard(lang))

@router.callback_query(
    lambda c: c.data in ["data_confirm_yes", "data_confirm_no"],
    InsuranceForm.data_review
)

async def process_data_review(callback_query: types.CallbackQuery,
                              state: FSMContext):
    """
    YES  → отправляем письмо и в канал.
    NO   → показываем клавиатуру выбора поля для исправления.
    """
    data = await state.get_data()
    lang = data.get("lang", "ru")

    # ------------------------------------------------- если пользователь нажал «Ні / No»
    if callback_query.data == "data_confirm_no":
        # поля, которые разрешено редактировать
        fields = [
            "birth_date",
            "full_name",
            "passport",
            "address",
            "gender",
            "citizenship",
            "phone",
            "email",
        ]
        await bot.send_message(
            callback_query.from_user.id,
            messages["edit_choose_field"][lang],
            reply_markup=error_fields_keyboard(fields, lang)
        )
        return  # остаёмся в состоянии data_review

    # ------------------------------------------------- если «Так / Yes» → собираем письмо
    policy_human = policy_map.get(data.get("policy"), {}).get(lang, data.get("policy"))
    term_human   = term_map.get(data.get("term"), {}).get(lang, data.get("term"))
    labels = messages["field_labels"][lang]

    summary = (
        f"{labels['policy_type']}: {policy_human}\n"
        f"{labels['policy_term']}: {term_human}\n"
        f"{labels['policy_start']}: {data.get('policy_start_date')}\n"
        f"{labels['policy_price']}: {data.get('price')} UAH\n"
        f"{field_names[lang]['full_name']}: {data.get('full_name')}\n"
        f"{field_names[lang]['birth_date']}: {data.get('birth_date')}\n"
        f"{field_names[lang]['passport']}: {data.get('passport')}\n"
        f"{field_names[lang]['address']}: {data.get('address')}\n"
        f"{labels['gender']}: {data.get('gender')}\n"
        f"{labels['citizenship']}: {data.get('citizenship')}\n"
        f"{field_names[lang]['phone']}: {data.get('phone')}\n"
        f"{field_names[lang]['email']}: {data.get('email')}"
    )

    # отправляем
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
    prompt_map = {
        "birth_date": messages["enter_birth_date"][lang],
        "full_name": messages["enter_full_name"][lang],
        "passport": messages["enter_passport"][lang],
        "phone": messages["enter_phone"][lang],
        "email": messages["enter_email"][lang],
        "address": messages["enter_address"][lang],
        "gender": messages["gender_prompt"][lang],
        "citizenship": messages["citizenship_prompt"][lang],
        "term": messages["term_choice"][lang],
    }
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
    if not isinstance(field, str):
        await message.answer(messages["edit_choose_field"][lang])
        return

    # ---------- сохраняем новое значение ----
    await state.update_data(**{field: message.text.strip()})

    # ---------- строим полное резюме ----
    data = await state.get_data()                 # перечитываем
    labels = messages["field_labels"][lang]

    policy_human = policy_map.get(data.get("policy"), {}).get(lang, data.get("policy"))
    term_human   = term_map.get(data.get("term"),   {}).get(lang, data.get("term"))

    summary = (
        f"{labels['policy_type']}: {policy_human}\n"
        f"{labels['policy_term']}: {term_human}\n"
        f"{labels['policy_start']}: {data.get('policy_start_date')}\n"
        f"{labels['policy_price']}: {data.get('price')} UAH\n"
        f"{field_names[lang]['full_name']}: {data.get('full_name')}\n"
        f"{field_names[lang]['birth_date']}: {data.get('birth_date')}\n"
        f"{field_names[lang]['passport']}: {data.get('passport')}\n"
        f"{field_names[lang]['address']}: {data.get('address')}\n"
        f"{labels['gender']}: {data.get('gender')}\n"
        f"{labels['citizenship']}: {data.get('citizenship')}\n"
        f"{field_names[lang]['phone']}: {data.get('phone')}\n"
        f"{field_names[lang]['email']}: {data.get('email')}\n"
)
    # фиксируем состояние, затем показываем ПОЛНОЕ резюме + кнопки
    await state.set_state(InsuranceForm.data_review)

    text = messages["data_review"][lang].format(data=summary)
    await bot.send_message(
        message.chat.id,
        text,
        reply_markup=data_confirmation_keyboard(lang)
)

