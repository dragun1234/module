# localization.py
messages = {
    "policy_start": {
        "uk": "Оберіть дату початку дії страхового полісу (ДД.ММ.РРРР):",
        "en": "Enter policy start date (DD.MM.YYYY):",
        "ru": "Введите дату начала действия полиса (ДД.ММ.ГГГГ):"
    },
     "policy_choice": {
        "uk": "Оберіть тип страхового полісу:",
        "en": "Choose the type of insurance policy:",
        "ru": "Выберите тип страхового полиса:"
    },
    "policy_button_visa_d": {
        "uk": "Поліс для візи D",
        "en": "Insurance for visa D",
        "ru": "Полис для визы D"
    },
    "policy_button_trp": {
        "uk": "Поліс для ВНЖ",
        "en": "Insurance for TRP",
        "ru": "Полис для ВНЖ"
    },
    "policy_button_visa_d_short": {
        "uk": "Visa D",
        "en": "Visa D",
        "ru": "Visa D"
    },
    "policy_button_trp_short": {
        "uk": "TRP",
        "en": "TRP",
        "ru": "TRP"
    },
    "field_labels": {
    "uk": {
        "policy_type": "Вид поліса",
        "policy_term": "Строк дії поліса",
        "policy_start": "Дата початку дії поліса",
        "policy_price": "Вартість поліса",
        "gender": "Стать",
        "citizenship": "Громадянство"
    },
    "en": {
        "policy_type": "Policy type",
        "policy_term": "Policy term",
        "policy_start": "Policy start date",
        "policy_price": "Policy price",
        "gender": "Gender",
        "citizenship": "Citizenship"
    },
    "ru": {
        "policy_type": "Вид полиса",
        "policy_term": "Срок действия полиса",
        "policy_start": "Дата начала действия полиса",
        "policy_price": "Стоимость полиса",
        "gender": "Пол",
        "citizenship": "Гражданство"
    }
},
    "term_choice": {
        "uk": "Оберіть строк дії полісу:",
        "en": "Choose the policy term:",
        "ru": "Выберите срок действия полиса:"
    },
    "citizenship_choice": {
        "uk": "Будь ласка, оберіть ваше громадянство:",
        "en": "Please choose your citizenship:",
        "ru": "Пожалуйста, выберите ваше гражданство:"
    },
    "consent_personal": {
        "uk": "Чи даєте Ви згоду на обробку персональних даних?",
        "en": "Do you consent to the processing of personal data?",
        "ru": "Вы даёте согласие на обработку персональных данных?"
    },
    "consent_contact": {
        "uk": "Чи дозволяєте Ви використання Вашого номера телефону та e-mail для підписання полісу?",
        "en": "Do you allow the use of your phone number and e-mail for signing the policy?",
        "ru": "Разрешаете ли Вы использовать ваш номер телефона и e-mail для оформления полиса?"
    },
    "enter_birth_date": {
        "uk": "Введіть дату народження у форматі ДД.ММ.РРРР:",
        "en": "Enter your birth date in DD.MM.YYYY format:",
        "ru": "Введите дату рождения в формате ДД.ММ.ГГГГ:"
    },
    "invalid_date": {
        "uk": "Неправильний формат дати. Введіть дату у форматі ДД.ММ.РРРР.",
        "en": "Invalid date format. Please enter the date in DD.MM.YYYY format.",
        "ru": "Неправильный формат даты. Введите дату в формате ДД.ММ.ГГГГ."
    },
    "age_error": {
        "uk": "На жаль, для оформлення полісу необхідно бути молодшим 70 років.",
        "en": "Unfortunately, you must be younger than 70 to be eligible for the policy.",
        "ru": "К сожалению, для оформления полиса необходимо быть моложе 70 лет."
    },
    "gender_prompt": {
    "uk": "Виберіть Вашу стать:",
    "en": "Choose your gender:",
    "ru": "Выберите ваш пол:"
    },
    "gender_female": {
    "uk": "Жіноча",
    "en": "Female",
    "ru": "Женский"
    },
    "gender_male": {
    "uk": "Чоловіча",
    "en": "Male",
    "ru": "Мужской"
    },
    "price_offer": {
        "uk": "Вартість полісу становить *{price}* грн. Чи приймаєте Ви цю ціну?",
        "en": "The policy price is *{price}*. Do you accept this price?",
        "ru": "Стоимость полиса составляет *{price}*. Принимаете ли Вы эту цену?"
    },
    "enter_full_name": {
        "uk": "Введіть Ваше ПІБ (тільки латинські літери):",
        "en": "Enter your full name (Latin letters only):",
        "ru": "Введите ваше ФИО (только латинские буквы):"
    },
    "invalid_full_name": {
        "uk": "Неправильний формат ПІБ. Спробуйте ще раз.",
        "en": "Invalid full name format. Please try again.",
        "ru": "Неправильный формат ФИО. Попробуйте снова."
    },
    "enter_passport": {
        "uk": "Введіть дані паспорта (тільки латинські літери та цифри):",
        "en": "Enter your passport details (Latin letters and digits only):",
        "ru": "Введите паспортные данные (только латинские буквы и цифры):"
    },
    "invalid_passport": {
        "uk": "Неправильний формат паспорта. Спробуйте ще раз.",
        "en": "Invalid passport format. Please try again.",
        "ru": "Неправильный формат паспорта. Попробуйте снова."
    },
    "enter_phone": {
        "uk": "Введіть номер українського мобільного телефону (Kyivstar, Vodafone, lifecell) у форматі +380XXXXXXXXX. Тільки 9 цифр після +380. Наприклад: +380931234567",
        "en": "Enter your Ukrainian mobile phone number (Kyivstar, Vodafone, lifecell) in the format +380XXXXXXXXX. Only 9 digits after +380. Example: +380931234567",
        "ru": "Введите номер украинского мобильного телефона (Kyivstar, Vodafone, lifecell) в формате +380XXXXXXXXX. Только 9 цифр после +380. Например: +380931234567"
    },
    "invalid_phone": {
        "uk": "Неправильний формат номера телефону. Спробуйте ще раз.",
        "en": "Invalid phone number format. Please try again.",
        "ru": "Неправильный формат номера телефона. Попробуйте снова."
    },
    "enter_email": {
        "uk": "Введіть електронну адресу:",
        "en": "Enter your email:",
        "ru": "Введите email:"
    },
    "invalid_email": {
        "uk": "Невірний формат електронної адреси. Спробуйте ще раз.",
        "en": "Invalid email format. Please try again.",
        "ru": "Неправильный формат email. Попробуйте снова."
    },
    "enter_address": {
        "uk": "Введіть адресу проживання:",
        "en": "Enter your residential address:",
        "ru": "Введите адрес проживания:"
    },
    "invalid_address": {
        "uk": "Неправильний формат адреси. Спробуйте ще раз.",
        "en": "Invalid address format. Please try again.",
        "ru": "Неправильный формат адреса. Попробуйте снова."
    },
    "data_review": {
        "uk": "Будь ласка, перевірте введені дані:\n{data}\nВсе вірно?",
        "en": "Please review your data:\n{data}\nIs everything correct?",
        "ru": "Пожалуйста, проверьте введённые данные:\n{data}\nВсё верно?"
    },
    "data_sent": {
        "uk": "Дані успішно відправлені!",
        "en": "Data has been successfully sent!",
        "ru": "Данные успешно отправлены!"
    },
        "edit_choose_field": {
        "uk": "Оберіть поле для виправлення:",
        "en": "Choose a field to edit:",
        "ru": "Выберите поле для исправления:"
    },
    "edit_enter_new": {
        "uk": "Введіть нове значення для {field}:",
        "en": "Enter new value for {field}:",
        "ru": "Введите новое значение для {field}:"
    },
        "data_confirm": {
        "uk": "Все вірно?",
        "en": "Is everything correct?",
        "ru": "Все верно?"
    },
    "operation_cancelled": {
        "uk": "Операцію скасовано.",
        "en": "Operation cancelled.",
        "ru": "Операция отменена."
    },
   "citizenship_prompt": {
    "uk": "Будь ласка, введіть ваше громадянство (назву країни):",
    "en": "Please enter your citizenship (country name):",
    "ru": "Пожалуйста, укажите ваше гражданство (название страны):"
},
"citizenship_invalid": {
    "uk": "Використовуйте лише літери українського алфавіту та пробіли.",
    "en": "Use letters of the English alphabet and spaces only.",
    "ru": "Используйте только буквы русского алфавита и пробелы."
},
"date_invalid": {
    "uk": "Невірний формат. Введіть ДД.ММ.РРРР.",
    "en": "Invalid format. Use DD.MM.YYYY.",
    "ru": "Неверный формат. Используйте ДД.ММ.ГГГГ."
},
"date_out_of_range": {
    "uk": "Дата має бути пізніше сьогодні, але не більше ніж через 3 роки.",
    "en": "Date must be after today but within 3 years.",
    "ru": "Дата должна быть позже сегодняшней, но не позднее 3 лет."
},
    "consent_yes": {
        "uk": "Так",
        "en": "Yes",
        "ru": "Да"
    },
    "consent_no": {
        "uk": "Ні",
        "en": "No",
        "ru": "Нет"
    },
    "price_confirm_yes": {
        "uk": "Так",
        "en": "Yes",
        "ru": "Да"
    },
    "price_confirm_no": {
        "uk": "Ні",
        "en": "No",
        "ru": "Нет"
    },
    "data_confirm_yes": {
        "uk": "Так",
        "en": "Yes",
        "ru": "Да"
    },
    "data_confirm_no": {
        "uk": "Ні",
        "en": "No",
        "ru": "Нет"
    },
    "choose_messenger": {
        "uk": "Виберіть тип мессенджера для зв'язку з вами:",
        "ru": "Выберите мессенджер для связи с вами:",
        "en": "Choose a messenger to contact you:"
    },
    "messenger_viber": {
        "uk": "Viber",
        "ru": "Viber",
        "en": "Viber"
    },
    "messenger_whatsapp": {
        "uk": "WhatsApp",
        "ru": "WhatsApp",
        "en": "WhatsApp"
    },
    "messenger_telegram": {
        "uk": "Telegram",
        "ru": "Telegram",
        "en": "Telegram"
    }
}
field_names = {
    "ru": {
        "birth_date": "Дата рождения",
        "full_name": "Полное имя",
        "passport": "Номер паспорта",
        "phone": "телефон",
        "email": "EMAIL",
        "address": "адрес",
        "messenger": "Мессенджер"
    },
    "en": {
        "birth_date": "Birth date",
        "full_name": "Full name",
        "passport": "Passport number",
        "phone": "Phone",
        "email": "Email",
        "address": "Address",
        "messenger": "Messenger"
    },
    "uk": {
        "birth_date": "Дата народження",
        "full_name": "ПІБ",
        "passport": "Номер паспорта",
        "phone": "Телефон",
        "email": "EMAIL",
        "address": "Адреса",
        "messenger": "Мессенджер"
    }
}