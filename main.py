import telebot
import pandas as pd
import json
from datetime import datetime

# Инициализация бота (замените токен на свой, но лучше вынести в config.py)
bot = telebot.TeleBot("8407192082:AAEuJ5nHN_HDoO4jcQVj0IQoidn9r9ZCUH8")

# --- Вспомогательные функции ---

def load_professions():
    """Загружает базу профессий из CSV."""
    return pd.read_csv('professions.csv')

# --- Главное меню и старт ---

def get_main_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🔎 Найти профессию")
    keyboard.add("📖 Узнать о профессиях подробнее")
    keyboard.add("⭐ Избранное", "📊 Статистика")
    keyboard.add("ℹ️ Помощь", "💬 Обратная связь")
    return keyboard

@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    bot.send_message(
        message.chat.id,
        f'Привет, {user.first_name}! 👋\n\n'
        'Я помогу тебе найти подходящую профессию. '
        'Выбери действие в меню ниже:',
        reply_markup=get_main_keyboard()
    )

# --- Обработка текстовых сообщений (меню) ---

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text

    if text == "🔎 Найти профессию":
        find_profession(message)
    elif text == "📖 Узнать о профессиях подробнее":
        show_professions(message)
    elif text == "⭐ Избранное":
        show_favorites(message)
    elif text == "📊 Статистика":
        show_statistics(message)
    elif text == "ℹ️ Помощь":
        help_command(message)
    elif text == "💬 Обратная связь":
        request_feedback(message)
    else:
        # Поиск по ключевым словам (если текст длиннее 2 символов)
        if len(text) > 2:
            search_professions(message, text)
        else:
            bot.send_message(message.chat.id, 'Используй кнопки меню для навигации.', reply_markup=get_main_keyboard())

# --- Сценарий «Найти профессию» (опрос) ---

def find_profession(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💻 Техника", "🎨 Творчество")
    markup.add("👥 Работа с людьми", "📊 Аналитика")
    bot.send_message(
        message.chat.id,
        'Ответь на несколько вопросов, чтобы получить персональные рекомендации!\n\n'
        'Что тебе больше нравится?',
        reply_markup=markup
    )
    bot.register_next_step_handler(message, handle_interests)

def handle_interests(message):
    interest = message.text
    # Здесь можно сохранять интерес в профиль пользователя, если нужно

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💡 Креативность", "🧠 Логика")
    markup.add("💬 Коммуникация", "🔢 Аналитика")
    bot.send_message(
        message.chat.id,
        'Отлично! А какие у тебя сильные стороны?',
        reply_markup=markup
    )
    bot.register_next_step_handler(message, lambda msg: handle_skills(msg, interest))

def handle_skills(message, interest):
    skill = message.text
    recommend_professions(message, interest, skill)

def recommend_professions(message, interest, skill):
    professions = load_professions()
    category_mapping = {
        '💻 Техника': 'IT',
        '🎨 Творчество': 'Творчество',
        '👥 Работа с людьми': 'Работа с людьми',
        '📊 Аналитика': 'Бизнес'
    }
    target_category = category_mapping.get(interest, 'IT')

    filtered = professions[professions['category'] == target_category]
    if filtered.empty:
        filtered = professions.head(3)

    response = '🎯 Вот несколько профессий, которые могут тебе подойти:\n\n'
    for _, prof in filtered.head(3).iterrows():
        response += (
            f'🔔 <b>{prof["profession"]}</b>\n'
            f'📝 {prof["description"]}\n'
            f'💰 Зарплата: {prof["salary"]} руб/мес\n'
            f'📚 Образование: {prof["education"]}\n'
            f'🛠️ Навыки: {prof["skills"]}\n\n'
        )

    bot.send_message(message.chat.id, response, parse_mode='HTML', reply_markup=get_main_keyboard())

# --- Детальный просмотр профессий (Inline-кнопки) ---

def show_professions(message):
    professions = load_professions()
    markup = telebot.types.InlineKeyboardMarkup()

    for _, prof in professions.iterrows():
        markup.add(telebot.types.InlineKeyboardButton(
            text=prof["profession"],
            callback_data=f"prof_{prof['id']}"
        ))

    bot.send_message(
        message.chat.id,
        '📚 Выбери профессию для подробной информации:',
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('prof_'))
def show_detailed_profession(call):
    prof_id = int(call.data.split('_'))
    professions = load_professions()
    prof = professions[professions['id'] == prof_id].iloc

    detailed_info = (
        f'<b>{prof["profession"]}</b>\n\n'
        f'📝 <b>Описание:</b> {prof["description"]}\n'
        f'💰 <b>Зарплата:</b> {prof["salary"]} руб/мес\n'
        f'📚 <b>Образование:</b> {prof["education"]}\n'
        f'🛠️ <b>Навыки:</b> {prof["skills"]}\n'
        f'🌍 <b>Востребованность:</b> {prof["demand"]}\n'
        f'🚀 <b>Перспективы:</b> {prof["prospects"]}\n'
    )

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        text="⭐ Добавить в избранное",
        callback_data=f"fav_{prof_id}"
    ))

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=detailed_info,
        parse_mode='HTML',
        reply_markup=markup
    )

# --- Избранное (добавление и просмотр) ---

@bot.callback_query_handler(func=lambda call: call.data.startswith('fav_'))
def add_to_favorites(call):
    user_id = call.from_user.id
    prof_id = int(call.data.split('_'))

    try:
        with open('favorites.json', 'r', encoding='utf-8') as f:
            favorites = json.load(f)
    except FileNotFoundError:
        favorites = {}

    if str(user_id) not in favorites:
        favorites[str(user_id)] = []

    if prof_id not in favorites[str(user_id)]:
        favorites[str(user_id)].append(prof_id)
        with open('favorites.json', 'w', encoding='utf-8') as f:
            json.dump(favorites, f, ensure_ascii=False, indent=2)
        bot.answer_callback_query(call.id, "Профессия добавлена в избранное! ✅")
    else:
        bot.answer_callback_query(call.id, "Эта профессия уже в избранном! ⚠️")

def show_favorites(message):
    try:
        with open('favorites.json', 'r', encoding='utf-8') as f:
            favorites = json.load(f)
    except FileNotFoundError:
        favorites = {}

    user_id = message.from_user.id
    if str(user_id) not in favorites or not favorites[str(user_id)]:
        bot.send_message(message.chat.id, "У вас пока нет избранных профессий. ⭐", reply_markup=get_main_keyboard())
        return

    professions = load_professions()
    favorite_list = favorites[str(user_id)]
    response = "⭐ Ваши избранные профессии:\n\n"

    for prof_id in favorite_list:
        prof = professions[professions['id'] == prof_id]
        if not prof.empty:
            prof = prof.iloc
            response += (
                f'🔔 <b>{prof["profession"]}</b>\n'
                f'📝 {prof["description"]}\n'
                f'💰 Зарплата: {prof["salary"]} руб/мес\n\n'
            )

    bot.send_message(message.chat.id, response, parse_mode='HTML', reply_markup=get_main_keyboard())

# --- Статистика ---

def show_statistics(message):
    professions = load_professions()
    stats = professions.groupby('category')['salary'].agg(['mean', 'count']).round(2)

    response = "📊 Статистика по профессиям:\n\n"
    for category, data in stats.iterrows():
        response += (
            f'🏢 <b>{category}</b>\n'
            f'• Средняя зарплата: {data["mean"]} руб\n'
            f'• Количество профессий: {data["count"]}\n\n'
        )

    total_professions = len(professions)
    avg_salary = professions['salary'].mean().round(2)

    response += (
        f'🧮 Общая статистика:\n'
        f'• Всего профессий в базе: {total_professions}\n'
        f'• Средняя зарплата по всем профессиям: {avg_salary} руб'
    )

    bot.send_message(message.chat.id, response, parse_mode='HTML', reply_markup=get_main_keyboard())

# --- Поиск по ключевым словам ---

def search_professions(message, query):
    professions = load_professions()
    filtered = professions[
        professions['profession'].str.contains(query, case=False, na=False) |
        professions['description'].str.contains(query, case=False, na=False)
    ]

    if filtered.empty:
        bot.send_message(
            message.chat.id,
            "По вашему запросу ничего не найдено. Попробуйте другой запрос.",
            reply_markup=get_main_keyboard()
        )
        return

    response = f"🔍 Результаты поиска по запросу «{query}»:\n\n"
    for _, prof in filtered.head(5).iterrows():
        response += (
            f'🔔 <b>{prof["profession"]}</b>\n'
            f'📝 {prof["description"][:100]}...\n'
            f'💰 Зарплата: {prof["salary"]} руб/мес\n\n'
        )

    bot.send_message(message.chat.id, response, parse_mode='HTML', reply_markup=get_main_keyboard())

# --- Обратная связь ---

def request_feedback(message):
    bot.send_message(
        message.chat.id,
        "Напишите ваш отзыв или предложение для улучшения бота:",
        reply_markup=telebot.types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(message, save_feedback)

def save_feedback(message):
    feedback_text = message.text
    user = message.from_user

    with open('feedback.txt', 'a', encoding='utf-8') as f:
        f.write(f"{datetime.now()} | {user.id} | {user.first_name}: {feedback_text}\n")

    bot.send_message(
        message.chat.id,
        "Спасибо за ваш отзыв! Мы обязательно его учтём. 🙏",
        reply_markup=get_main_keyboard()
    )

# --- Помощь ---

def help_command(message):
    help_text = '''🤖 <b>Помощь по боту</b>

<b>Доступные команды:</b>
🔎 <b>Найти профессию</b> — пройти опрос и получить рекомендации
📖 <b>Узнать о профессиях подробнее</b> — список всех профессий с детальной информацией
⭐ <b>Избранное</b> — ваши сохранённые профессии
📊 <b>Статистика</b> — средние зарплаты и количество профессий по категориям
ℹ️ <b>Помощь</b> — эта справка
💬 <b>Обратная связь</b> — оставить отзыв о боте

Также вы можете искать профессии по ключевым словам!

Просто выбери нужную кнопку в меню!'''

    bot.send_message(message.chat.id, help_text, parse_mode='HTML')

# --- Запуск ---

if __name__ == '__main__':
    print("Бот запускается...")
    try:
        # timeout=60 даёт больше времени на соединение, long_polling_timeout=60 уменьшает частоту запросов
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"Критическая ошибка соединения: {e}")
        print("Проверьте интернет или настройки прокси.")

