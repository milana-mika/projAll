import telebot
from telebot import types
from tok import TOKEN

bot = telebot.TeleBot(TOKEN)

# Расписание звонков и перемен (обычный текст без опасных тегов)
SCHEDULE_BREAKS = (
    "🔔 Расписание звонков и перемен:\n\n"
    "1 урок: 08:30 — 09:15\n"
    "• Перемена: 10 минут\n"
    "2 урок: 09:25 — 10:10\n"
    "• Перемена: 20 минут (Большая)\n"
    "3 урок: 10:30 — 11:15\n"
    "• Перемена: 15 минут\n"
    "4 урок: 11:30 — 12:15\n"
    "• Перемена: 20 минут (Большая)\n"
    "5 урок: 12:35 — 13:20\n"
    "• Перемена: 10 минут\n"
    "6 урок: 13:30 — 14:15\n"
    "• Перемена: 10 минут\n"
    "7 урок: 14:25 — 15:10"
)

# Базовое расписание уроков на всю неделю
SCHEDULE_DAYS = {
    "Понедельник": (
        "📅 Расписание на Понедельник:\n\n"
        "1. Разговоры о важном\n"
        "2. Математика\n"
        "3. Русский язык\n"
        "4. Физика\n"
        "5. История\n"
        "6. Физкультура"
    ),
    "Вторник": (
        "📅 Расписание на Вторник:\n\n"
        "1. Английский язык\n"
        "2. Алгебра\n"
        "3. Геометрия\n"
        "4. Химия\n"
        "5. Биология\n"
        "6. Литература"
    ),
    "Среда": (
        "📅 Расписание на Среда:\n\n"
        "1. Обществознание\n"
        "2. Русский язык\n"
        "3. Литература\n"
        "4. Информатика\n"
        "5. Физика\n"
        "6. География"
    ),
    "Четверг": (
        "📅 Расписание на Четверг:\n\n"
        "1. Алгебра\n"
        "2. Английский язык\n"
        "3. Химия\n"
        "4. История\n"
        "5. ОБЖ\n"
        "6. Физкультура"
    ),
    "Пятница": (
        "📅 Расписание на Пятница:\n\n"
        "1. Биология\n"
        "2. Геометрия\n"
        "3. Русский язык\n"
        "4. Литература\n"
        "5. Технология / Труд\n"
        "6. Музыка / ИЗО"
    ),
    "Суббота": (
        "📅 Расписание на Суббота:\n\n"
        "1. Электив по математике\n"
        "2. Физический практикум\n"
        "3. Классный час"
    ),
}

user_states = {}


def get_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_mon = types.KeyboardButton("Понедельник")
    btn_tue = types.KeyboardButton("Вторник")
    btn_wed = types.KeyboardButton("Среда")
    btn_thu = types.KeyboardButton("Четверг")
    btn_fri = types.KeyboardButton("Пятница")
    btn_sat = types.KeyboardButton("Суббота")
    btn_breaks = types.KeyboardButton("🔔 Звонки и перемены")
    btn_edit = types.KeyboardButton("✏️ Изменить расписание")

    markup.add(btn_mon, btn_tue)
    markup.add(btn_wed, btn_thu)
    markup.add(btn_fri, btn_sat)
    markup.add(btn_breaks, btn_edit)
    return markup


def get_days_inline_keyboard():
    markup = types.InlineKeyboardMarkup()
    for day in SCHEDULE_DAYS.keys():
        markup.add(types.InlineKeyboardButton(text=day, callback_data=f"edit_{day}"))
    return markup


@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.from_user.id
    user_states[user_id] = {"state": None}
    bot.send_message(
        message.chat.id,
        "Привет! 👋 Я бот-расписание.\n"
        "Выбери нужный день недели или посмотри расписание звонков с помощью кнопок ниже 👇",
        reply_markup=get_keyboard(),
    )


@bot.message_handler(func=lambda message: message.text == "✏️ Изменить расписание")
def start_edit(message):
    user_id = message.from_user.id
    user_states[user_id] = {"state": "selecting_day"}
    bot.send_message(
        message.chat.id,
        "Выбери день недели, расписание которого хочешь изменить:",
        reply_markup=get_days_inline_keyboard(),
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("edit_"))
def callback_edit_day(call):
    user_id = call.from_user.id
    day = call.data.split("_")[1]
    user_states[user_id] = {"state": "waiting_new_schedule", "day_to_edit": day}

    bot.answer_callback_query(call.id)
    bot.send_message(
        call.message.chat.id,
        f"Ты выбрал: <b>{day}</b>.\n\n"
        "Отправь новое расписание для этого дня одним сообщением:",
        parse_mode="HTML"
    )


@bot.message_handler(
    func=lambda message: message.text in SCHEDULE_DAYS or message.text == "🔔 Звонки и перемены"
)
def handle_schedule(message):
    user_id = message.from_user.id
    if user_id in user_states and user_states[user_id].get("state") == "waiting_new_schedule":
        save_new_schedule(message)
        return

    text = message.text
    if text == "🔔 Звонки и перемены":
        bot.send_message(message.chat.id, SCHEDULE_BREAKS, reply_markup=get_keyboard())
    elif text in SCHEDULE_DAYS:
        bot.send_message(message.chat.id, SCHEDULE_DAYS[text], reply_markup=get_keyboard())


@bot.message_handler(func=lambda message: True)
def handle_other_messages(message):
    user_id = message.from_user.id
    if user_id in user_states and user_states[user_id].get("state") == "waiting_new_schedule":
        save_new_schedule(message)
        return

    bot.reply_to(
        message,
        "Пожалуйста, используй кнопки меню для просмотра или изменения расписания.",
        reply_markup=get_keyboard(),
    )


def save_new_schedule(message):
    user_id = message.from_user.id
    day = user_states[user_id]["day_to_edit"]
    new_text = message.text.strip()

    # Сохраняем без принудительного HTML-парсинга, чтобы не было ошибок 400
    SCHEDULE_DAYS[day] = f"📅 Расписание на {day} (изменено):\n\n{new_text}"
    user_states[user_id] = {"state": None}

    bot.send_message(
        message.chat.id,
        f"✅ Расписание на {day} успешно обновлено!",
        reply_markup=get_keyboard(),
    )


if __name__ == "__main__":
    print("Бот с расписанием и функцией редактирования запущен...")
    bot.infinity_polling()