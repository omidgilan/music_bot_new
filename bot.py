import telebot
from telebot import types

# 🔹 توکن ربات
TOKEN = "5548149661:AAFblu4NL86utR9SbzuE6RQ27HuD3Uiynas"
bot = telebot.TeleBot(TOKEN)

# 🔹 دیکشنری آهنگ‌ها (نام آهنگ و لینک فایل تلگرام و لینک عکس)
songs = {
    "معین - آرزو داشتم": {
        "file": "https://t.me/solfg0_filebot/20",
        "thumb": "https://i.ibb.co/TMJLFKHZ/IMG-20251026-000741-631.jpg"
    },
    "معین - کعبه": {
        "file": "https://t.me/solfg0_filebot/23",
        "thumb": "https://i.ibb.co/KTLVWDk/IMG-20251026-032304-853.jpg"
    },
    "معین - مست": {
        "file": "https://t.me/solfg0_filebot/25",
        "thumb": "https://i.ibb.co/Hp36wWKT/images.jpg"
    },
    "معین - قسم به عشقمون": {
        "file": "https://t.me/solfg0_filebot/46",
        "thumb": "https://i.ibb.co/PsCdG52g/images-1.jpg"
    }
}

# ======= آینلاین کوئری =======
@bot.inline_handler(lambda query: True)
def inline_query_handler(inline_query):
    results = []
    for name, info in songs.items():
        # هر آیتم آینلاین با دکمه شیشه‌ای برای رفتن به چت ربات
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(
            text="باز کردن در ربات",
            switch_inline_query_current_chat=name
        )
        markup.add(btn)

        results.append(types.InlineQueryResultArticle(
            id=name,
            title=name,
            description="کلیک کنید برای دریافت آهنگ",
            input_message_content=types.InputTextMessageContent(
                message_text=f"{name}\n{info['file']}"
            ),
            thumbnail_url=info['thumb'],
            reply_markup=markup
        ))
    bot.answer_inline_query(inline_query.id, results, cache_time=0)

# ======= چت ربات =======
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        text="جستجو آهنگ‌ها",
        switch_inline_query_current_chat=""
    )
    markup.add(btn)
    bot.send_message(message.chat.id, "سلام! برای پیدا کردن آهنگ‌ها روی دکمه زیر بزنید:", reply_markup=markup)

# ======= شروع ربات =======
bot.infinity_polling()
