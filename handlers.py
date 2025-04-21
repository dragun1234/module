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
    citizenship_keyboard,
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

router = Router()

class InsuranceForm(StatesGroup):
    language = State()   # Шаг 1: Выбор языка
    policy_type = State()  # Тип полиса
    term = State()  # Срок действия
    citizenship = State()  # Гражданство
    consent_personal = State()
    consent_contact = State()
    birth_date = State()
    price_confirmation = State()
    full_name = State()
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
    await message.answer(messages["start"]["🇺🇦 Українська"], reply_markup=language_keyboard())

@router.callback_query(lambda c: c.data.startswith("lang_"), InsuranceForm.language)
async def process_language(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора языка."""
    lang_code = callback_query.data.split("_")[1]
    lang_map = {"uk": "🇺🇦 Українська", "en": "🇬🇧 English", "ru": "🇷🇺 Русский"}
    selected_lang = lang_map.get(lang_code, "🇷🇺 Русский")
    # Сохраняем выбранный язык в состояние
    await state.update_data(lang=selected_lang)
    print(f"[DEBUG] Selected language: {selected_lang}")  # Отладочный вывод
    text = messages["policy_choice"][selected_lang]
    await bot.send_message(callback_query.from_user.id, text, reply_markup=policy_type_keyboard(selected_lang))
    await state.set_state(InsuranceForm.policy_type)

@router.callback_query(lambda c: c.data.startswith("policy_"), InsuranceForm.policy_type)
async def process_policy(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора типа полиса."""
    policy = callback_query.data
    await state.update_data(policy=policy)
    data = await state.get_data()
    lang = data.get("lang", "🇷🇺 Русский")  # Получение языка из состояния
    print(f"[DEBUG] Current lang in policy_type: {lang}")  # Отладочный вывод
    text = messages["term_choice"][lang]
    await bot.send_message(callback_query.from_user.id, text, reply_markup=term_keyboard(lang))  # Передаём lang в term_keyboard
    await state.set_state(InsuranceForm.term)

@router.callback_query(lambda c: c.data.startswith("term_"), InsuranceForm.term)
async def process_term(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора срока действия."""
    term = callback_query.data.split("_")[1]
    await state.update_data(term=term)
    data = await state.get_data()
    lang = data.get("lang", "🇷🇺 Русский")  # Получение языка из состояния
    print(f"[DEBUG] Current lang in term: {lang}")  # Отладочный вывод
    text = messages["citizenship_choice"][lang]
    await bot.send_message(callback_query.from_user.id, text, reply_markup=citizenship_keyboard(lang))  # Передаём lang в citizenship_keyboard
    await state.set_state(InsuranceForm.citizenship)

@router.callback_query(lambda c: c.data.startswith("citizenship_"), InsuranceForm.citizenship)
async def process_citizenship(callback_query: types.CallbackQuery, state: FSMContext):
    """Обработка выбора гражданства."""
    citizenship = callback_query.data.split("_")[1]
    await state.update_data(citizenship=citizenship)
    data = await state.get_data()
    lang = data.get("lang", "🇷🇺 Русский")
    print(f"[DEBUG] Current lang in citizenship: {lang}")  # Отладочный вывод
    text = messages["consent_personal"][lang]
    await bot.send_message(callback_query.from_user.id, text, reply_markup=consent_keyboard(lang))
    await state.set_state(InsuranceForm.consent_personal)

@router.callback_query(lambda c: c.data in ["consent_yes", "consent_no"], InsuranceForm.consent_personal)
async def process_consent_personal(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "consent_no":
        data = await state.get_data()
        lang = data.get("lang", "🇷🇺 Русский")
        await bot.send_message(callback_query.from_user.id, messages["operation_cancelled"][lang])
        await state.clear()
    else:
        data = await state.get_data()
        lang = data.get("lang", "🇷🇺 Русский")
        text = messages["consent_contact"][lang]
        await bot.send_message(callback_query.from_user.id, text, reply_markup=consent_keyboard(lang))
        await state.set_state(InsuranceForm.consent_contact)

@router.callback_query(lambda c: c.data in ["consent_yes", "consent_no"], InsuranceForm.consent_contact)
async def process_consent_contact(callback_query: types.CallbackQuery, state: FSMContext):
    if callback_query.data == "consent_no":
        data = await state.get_data()
        lang = data.get("lang", "🇷🇺 Русский")
        await bot.send_message(callback_query.from_user.id, messages["operation_cancelled"][lang])
        await state.clear()
    else:
        data = await state.get_data()
        lang = data.get("lang", "🇷🇺 Русский")
        text = messages["enter_birth_date"][lang]
        await bot.send_message(callback_query.from_user.id, text)
        await state.set_state(InsuranceForm.birth_date)

@router.message(InsuranceForm.birth_date)
async def process_birth_date(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "🇷🇺 Русский")
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
    term = data.get("term")
    policy = data.get("policy")
    
    base_price = 1500 if policy == "policy_visa_d" else 1200
    multiplier = {"1_month": 1, "6_months": 5, "1_year": 10}.get(term, 1)
    price = base_price * multiplier
    if age > 60:
        price *= 1.5
    await state.update_data(price=price)
    text = messages["price_offer"][lang].format(price=price)
    await message.answer(text, reply_markup=price_confirmation_keyboard(lang))
    await state.set_state(InsuranceForm.price_confirmation)

@router.callback_query(lambda c: c.data in ["price_confirm_yes", "price_confirm_no"], InsuranceForm.price_confirmation)
async def process_price_confirmation(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "🇷🇺 Русский")
    if callback_query.data == "price_confirm_no":
        await bot.send_message(callback_query.from_user.id, messages["operation_cancelled"][lang])
        await state.clear()
    else:
        await bot.send_message(callback_query.from_user.id, messages["enter_full_name"][lang])
        await state.set_state(InsuranceForm.full_name)

@router.message(InsuranceForm.full_name)
async def process_full_name(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "🇷🇺 Русский")
    if not validate_full_name(message.text):
        await message.answer(messages["invalid_full_name"][lang])
        return
    await state.update_data(full_name=message.text)
    await message.answer(messages["enter_passport"][lang])
    await state.set_state(InsuranceForm.passport)

@router.message(InsuranceForm.passport)
async def process_passport(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "🇷🇺 Русский")
    if not validate_passport(message.text):
        await message.answer(messages["invalid_passport"][lang])
        return
    await state.update_data(passport=message.text)
    await message.answer(messages["enter_phone"][lang])
    await state.set_state(InsuranceForm.phone)

@router.message(InsuranceForm.phone)
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "🇷🇺 Русский")
    if not validate_phone(message.text):
        await message.answer(messages["invalid_phone"][lang])
        return
    await state.update_data(phone=message.text)
    await message.answer(messages["enter_email"][lang])
    await state.set_state(InsuranceForm.email)

@router.message(InsuranceForm.email)
async def process_email(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "🇷🇺 Русский")
    if not validate_email(message.text):
        await message.answer(messages["invalid_email"][lang])
        return
    await state.update_data(email=message.text)
    await message.answer(messages["enter_address"][lang])
    await state.set_state(InsuranceForm.address)

@router.message(InsuranceForm.address)
async def process_address(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "🇷🇺 Русский")
    if not validate_address(message.text):
        await message.answer(messages["invalid_address"][lang])
        return
    await state.update_data(address=message.text)
    data = await state.get_data()
    summary = f"*{field_names[lang]['birth_date']}*: {data.get('birth_date')}\n" \
              f"*{field_names[lang]['full_name']}*: {data.get('full_name')}\n" \
              f"*{field_names[lang]['passport']}*: {data.get('passport')}\n" \
              f"*{field_names[lang]['phone']}*: {data.get('phone')}\n" \
              f"*{field_names[lang]['email']}*: {data.get('email')}\n" \
              f"*{field_names[lang]['address']}*: {data.get('address')}"
    text = messages["data_review"][lang].format(data=summary)
    await message.answer(text, reply_markup=data_confirmation_keyboard(lang))
    await state.set_state(InsuranceForm.data_review)

@router.callback_query(lambda c: c.data in ["data_confirm_yes", "data_confirm_no"], InsuranceForm.data_review)
async def process_data_review(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data.get("lang", "🇷🇺 Русский")
    if callback_query.data == "data_confirm_no":
        error_fields = ["birth_date", "full_name", "passport", "phone", "email", "address"]
        kb = error_fields_keyboard(error_fields, lang)
        await bot.send_message(callback_query.from_user.id, "Выберите поле для исправления:", reply_markup=kb)
    else:
        summary = f"Дата рождения: {data.get('birth_date')}\n" \
                  f"Полное имя: {data.get('full_name')}\n" \
                  f"Номер паспорта: {data.get('passport')}\n" \
                  f"Телефон: {data.get('phone')}\n" \
                  f"EMAIL: {data.get('email')}\n" \
                  f"адресс: {data.get('address')}"
        subject = "Новые данные для страхового полиса"
        await send_email(subject, summary, "igor@yrin.com")
        await send_channel_message(summary)
        await bot.send_message(callback_query.from_user.id, messages["data_sent"][lang])
        await state.clear()

@router.callback_query(lambda c: c.data.startswith("edit_"), InsuranceForm.data_review)
async def process_field_correction(callback_query: types.CallbackQuery, state: FSMContext):
    field = callback_query.data.split("edit_")[1]
    data = await state.get_data()
    lang = data.get("lang", "🇷🇺 Русский")
    prompt_map = {
        "birth_date": messages["enter_birth_date"][lang],
        "full_name": messages["enter_full_name"][lang],
        "passport": messages["enter_passport"][lang],
        "phone": messages["enter_phone"][lang],
        "email": messages["enter_email"][lang],
        "address": messages["enter_address"][lang]
    }
    prompt = prompt_map.get(field, "Введите значение:")
    await bot.send_message(callback_query.from_user.id, f"Введите новое значение для {field}:\n{prompt}")
    await state.update_data(correction_field=field)
    await state.set_state(InsuranceForm.correction)

@router.message(InsuranceForm.correction)
async def process_field_update(message: types.Message, state: FSMContext):
    data = await state.get_data()
    field = data.get("correction_field")
    lang = data.get("lang", "🇷🇺 Русский")
    if field == "birth_date":
        bd = validate_date(message.text)
        if not bd:
            await message.answer(messages["invalid_date"][lang])
            return
        age = calculate_age(bd)
        if age > 70:
            await message.answer(messages["age_error"][lang])
            await state.clear()
            return
        await state.update_data(birth_date=message.text, age=age)
    elif field == "full_name":
        if not validate_full_name(message.text):
            await message.answer(messages["invalid_full_name"][lang])
            return
        await state.update_data(full_name=message.text)
    elif field == "passport":
        if not validate_passport(message.text):
            await message.answer(messages["invalid_passport"][lang])
            return
        await state.update_data(passport=message.text)
    elif field == "phone":
        if not validate_phone(message.text):
            await message.answer(messages["invalid_phone"][lang])
            return
        await state.update_data(phone=message.text)
    elif field == "email":
        if not validate_email(message.text):
            await message.answer(messages["invalid_email"][lang])
            return
        await state.update_data(email=message.text)
    elif field == "address":
        if not validate_address(message.text):
            await message.answer(messages["invalid_address"][lang])
            return
        await state.update_data(address=message.text)
    await state.set_state(InsuranceForm.data_review)
    data = await state.get_data()
    summary = f"*{field_names[lang]['birth_date']}*: {data.get('birth_date')}\n" \
              f"*{field_names[lang]['full_name']}*: {data.get('full_name')}\n" \
              f"*{field_names[lang]['passport']}*: {data.get('passport')}\n" \
              f"*{field_names[lang]['phone']}*: {data.get('phone')}\n" \
              f"*{field_names[lang]['email']}*: {data.get('email')}\n" \
              f"*{field_names[lang]['address']}*: {data.get('address')}"
    text = messages["data_review"][lang].format(data=summary)
    await message.answer(text, reply_markup=data_confirmation_keyboard(lang))

