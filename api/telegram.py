import telebot
from telebot import types

TOKEN = "5548149661:AAFblu4NL86utR9SbzuE6RQ27HuD3Uiynas"
bot = telebot.TeleBot(TOKEN)

# دیکشنری آهنگ‌ها بر اساس خواننده
songs = {
    "معین": [
        {
            "name": "آرزو داشتم",
            "file": "https://t.me/solfg0_filebot/20",
            "thumb": "https://i.ibb.co/TMJLFKHZ/IMG-20251026-000741-631.jpg"
        },
        {
            "name": "کعبه",
            "file": "https://t.me/solfg0_filebot/23",
            "thumb": "https://i.ibb.co/KTLVWDk/IMG-20251026-032304-853.jpg"
        },
        {
            "name": "مست",
            "file": "https://t.me/solfg0_filebot/25",
            "thumb": "https://i.ibb.co/Hp36wWKT/images.jpg"
        },
        {
            "name": "قسم به عشقمون",
            "file": "https://t.me/solfg0_filebot/46",
            "thumb": "https://i.ibb.co/PsCdG52g/images-1.jpg"
        },
        {
            "name": "وقتی که تو رفتی",
            "file": "https://t.me/solfg0_filebot/53",
            "thumb": "https://i.ibb.co/prnk7QHn/images-1.jpg"
        }
    ]
}

# ======= هندلر آینلاین =======
@bot.inline_handler(lambda query: True)
def inline_query_handler(inline_query):
    query_text = inline_query.query.strip()
    results = []

    if query_text in songs:
        for song in songs[query_text]:
            markup = types.InlineKeyboardMarkup()
            btn = types.InlineKeyboardButton(
                text=song["name"],
                url=song["file"]  # لینک فایل تلگرام روی دکمه
            )
            markup.add(btn)

            results.append(types.InlineQueryResultArticle(
                id=song["name"],
                title=song["name"],
                description="کلیک کنید برای دریافت آهنگ",
                input_message_content=types.InputTextMessageContent(
                    message_text=f"{song['name']}\n{song['file']}"
                ),
                thumbnail_url=song["thumb"],
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
