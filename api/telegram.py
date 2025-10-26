import telebot
from telebot import types

# 🔹 توکن ربات
TOKEN = "5548149661:AAFblu4NL86utR9SbzuE6RQ27HuD3Uiynas"
bot = telebot.TeleBot(TOKEN)

# 🔹 دیکشنری آهنگ‌ها
songs = {
    "معین - آرزو داشتم": "https://t.me/solfg0_filebot/20",
    "معین - کعبه": "https://t.me/solfg0_filebot/23",
    "معین - مست": "https://t.me/solfg0_filebot/25",
    "معین - قسم به عشقمون": "https://t.me/solfg0_filebot/46",
    "معین - طناز": "https://t.me/solfg0_filebot/49",
    "معین - وقتی که تو رفتی": "https://t.me/solfg0_filebot/53",
    "معین - من باهاتم": "https://t.me/solfg0_filebot/55",
    "معین - دعای شب": "https://t.me/solfg0_filebot/60"
}

# ======= شروع پیام خوشامد =======
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "سلام! نام خواننده یا آهنگ را ارسال کنید تا نتایج برای شما نمایش داده شود.")

# ======= جستجو و دکمه شیشه‌ای =======
@bot.message_handler(func=lambda message: True)
def search_songs(message):
    query = message.text.lower()
    results = {name: link for name, link in songs.items() if query in name.lower()}

    if not results:
        bot.send_message(message.chat.id, "هیچ نتیجه‌ای یافت نشد.")
        return

    # متن بالای دکمه‌ها
    bot.send_message(message.chat.id, f"نتایج جستجو برای '{message.text}':")

    # ساخت کیبرد شیشه‌ای
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for name, link in results.items():
        btn = types.KeyboardButton(f"{name} - دریافت آهنگ")
        markup.add(btn)

    bot.send_message(message.chat.id, "برای دریافت آهنگ روی دکمه زیر بزنید:", reply_markup=markup)

# ======= ارسال لینک آهنگ وقتی دکمه زده شد =======
@bot.message_handler(func=lambda message: message.text.endswith("- دریافت آهنگ"))
def send_song_link(message):
    name = message.text.replace(" - دریافت آهنگ", "")
    if name in songs:
        bot.send_message(message.chat.id, songs[name])
    else:
        bot.send_message(message.chat.id, "خطا: آهنگ پیدا نشد.")

# ======= شروع ربات =======
bot.infinity_polling()
