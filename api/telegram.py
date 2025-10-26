import telebot
from telebot import types

TOKEN = "5548149661:AAFblu4NL86utR9SbzuE6RQ27HuD3Uiynas"
bot = telebot.TeleBot(TOKEN)

# دیکشنری آهنگ‌ها
songs = {
    "معین - آرزو داشتم": {"file": "https://t.me/solfg0_filebot/20", "thumb": "https://i.ibb.co/TMJLFKHZ/IMG-20251026-000741-631.jpg"},
    "معین - کعبه": {"file": "https://t.me/solfg0_filebot/23", "thumb": "https://i.ibb.co/KTLVWDk/IMG-20251026-032304-853.jpg"},
    "معین - مست": {"file": "https://t.me/solfg0_filebot/25", "thumb": "https://i.ibb.co/Hp36wWKT/images.jpg"},
    "معین - قسم به عشقمون": {"file": "https://t.me/solfg0_filebot/46", "thumb": "https://i.ibb.co/PsCdG52g/images-1.jpg"},
    "معین - طناز": {"file": "https://t.me/solfg0_filebot/49", "thumb": "https://i.ibb.co/ccs62YZp/images.jpg"},
    "معین - وقتی که تو رفتی": {"file": "https://t.me/solfg0_filebot/53", "thumb": "https://i.ibb.co/prnk7QHn/images-1.jpg"},
    "معین - من باهاتم": {"file": "https://t.me/solfg0_filebot/55", "thumb": "https://i.ibb.co/HDt4JXSV/images-2.jpg"},
    "معین - دعای شب": {"file": "https://t.me/solfg0_filebot/60", "thumb": "https://i.ibb.co/gM4K5rtg/images-3.jpg"}
}

# ===== آینلاین کوئری سریع =====
@bot.inline_handler(lambda query: True)
def inline_query_handler(inline_query):
    text = inline_query.query.lower()
    results = []
    for name, info in songs.items():
        if text in name.lower():
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text="دریافت آهنگ", callback_data=name))
            results.append(types.InlineQueryResultArticle(
                id=name, title=name, description="کلیک کنید برای دریافت آهنگ",
                input_message_content=types.InputTextMessageContent(f"{name}\n{info['file']}"),
                thumbnail_url=info['thumb'], reply_markup=markup
            ))
    bot.answer_inline_query(inline_query.id, results, cache_time=0)

# ===== جستجو در چت ربات =====
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    query = message.text.lower()
    matching = {n: i for n, i in songs.items() if query in n.lower()}
    if matching:
        markup = types.InlineKeyboardMarkup()
        for n in matching.keys():
            markup.add(types.InlineKeyboardButton(text=n, callback_data=n))
        bot.send_message(message.chat.id, f"نتایج جستجو برای '{message.text}':", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, f"نتیجه‌ای برای '{message.text}' پیدا نشد.")

# ===== دکمه شیشه‌ای callback =====
@bot.callback_query_handler(func=lambda c: True)
def callback_handler(call):
    name = call.data
    if name in songs:
        info = songs[name]
        # ارسال آهنگ همراه با دکمه شیشه‌ای همانجا
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton(text="دریافت دوباره", callback_data=name))
        bot.send_message(call.message.chat.id, f"{name}\n{info['file']}", reply_markup=markup)
        bot.answer_callback_query(call.id, text=f"آهنگ '{name}' ارسال شد")

# ===== شروع ربات =====
bot.infinity_polling()
