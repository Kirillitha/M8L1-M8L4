import telebot
import pandas as pd

# Инициализация бота (замените 'YOUR_TOKEN' на реальный токен)
bot = telebot.TeleBot("8407192082:AAEuJ5nHN_HDoO4jcQVj0IQoidn9r9ZCUH8")

# Загрузка базы профессий
def load_professions():
    return pd.read_csv('professions.csv')

# Главное меню
def get_main_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🔎 Найти профессию")
    keyboard.add("📖 Узнать о профессиях подробнее")
    keyboard.add("ℹ️ Помощь")
    return keyboard

# Команда /start
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

# Обработка текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text

    if text == "🔎 Найти профессию":
        find_profession(message)
    elif text == "📖 Узнать о профессиях подробнее":
        show_professions(message)
    elif text == "ℹ️ Помощь":
        help_command(message)
    else:
        bot.send_message(message.chat.id, 'Используй кнопки меню для навигации.')

# Сценарий «Найти профессию»
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

# Подбор профессий
def recommend_professions(message, interest, skill):
    professions = load_professions()

    # Простой алгоритм подбора: ищем профессии по категории интереса
    category_mapping = {
        '💻 Техника': 'IT',
        '🎨 Творчество': 'Творчество',
        '👥 Работа с людьми': 'Работа с людьми',
        '📊 Аналитика': 'Бизнес'
    }
    target_category = category_mapping.get(interest, 'IT')

    filtered = professions[professions['category'] == target_category]
    if filtered.empty:
        filtered = professions.head(3)  # Если нет совпадений, берём первые 3

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

# Сценарий «Узнать о профессиях подробнее»
def show_professions(message):
    professions = load_professions()
    response = '📚 Доступные профессии:\n\n'
    for _, prof in professions.iterrows():
        response += f'• <b>{prof["profession"]}</b> — {prof["description"]}\n'

    bot.send_message(message.chat.id, response, parse_mode='HTML')

# Сценарий «Помощь»
def help_command(message):
    help_text = '''🤖 <b>Помощь по боту</b>

<b>Доступные команды:</b>
🔎 <b>Найти профессию</b> — пройти опрос и получить рекомендации
📖 <b>Узнать о профессиях подробнее</b> — список всех профессий
ℹ️ <b>Помощь</b> — эта справка

Просто выбери нужную кнопку в меню!'''


    bot.send_message(message.chat.id, help_text, parse_mode='HTML')

# Запуск бота
if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()
