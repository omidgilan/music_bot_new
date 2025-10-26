import telebot
from telebot import types
import threading

# 🔹 توکن ربات
TOKEN = "5548149661:AAFblu4NL86utR9SbzuE6RQ27HuD3Uiynas"
bot = telebot.TeleBot(TOKEN)

# 🔹 دیکشنری آهنگ‌ها
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
    },
    "معین - طناز": {
        "file": "https://t.me/solfg0_filebot/49",
        "thumb": "https://i.ibb.co/ccs62YZp/images.jpg"
    },
    "معین - وقتی که تو رفتی": {
        "file": "https://t.me/solfg0_filebot/53",
        "thumb": "https://i.ibb.co/prnk7QHn/images-1.jpg"
    },
    "معین - من باهاتم": {
        "file": "https://t.me/solfg0_filebot/55",
        "thumb": "https://i.ibb.co/HDt4JXSV/images-2.jpg"
    },
    "معین - دعای شب": {
        "file": "https://t.me/solfg0_filebot/60",
        "thumb": "https://i.ibb.co/gM4K5rtg/images-3.jpg"
    }
}

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

# ======= جستجوی متن کاربر با پردازش سریع =======
@bot.message_handler(func=lambda m: True)
def search_songs(message):
    query = message.text.lower()
    matched = {name: info for name, info in songs.items() if query in name.lower()}

    if not matched:
        bot.send_message(message.chat.id, "آهنگی پیدا نشد 😕")
        return

    # ایجاد لیست شیشه‌ای
    markup = types.InlineKeyboardMarkup()
    for name in matched.keys():
        btn = types.InlineKeyboardButton(
            text=name,
            callback_data=name
        )
        markup.add(btn)

    bot.send_message(message.chat.id, f"نتایج جستجو برای: {message.text}", reply_markup=markup)

# ======= دریافت کلیک روی دکمه شیشه‌ای با ارسال سریع =======
@bot.callback_query_handler(func=lambda call: True)
def callback_song(call):
    info = songs.get(call.data)
    if info:
        threading.Thread(target=send_song, args=(call, info)).start()

def send_song(call, info):
    markup = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(
        text="باز کردن در ربات",
        switch_inline_query_current_chat=call.data
    )
    markup.add(btn)

    bot.send_message(call.message.chat.id, f"{call.data}\n{info['file']}", reply_markup=markup)

# ======= آینلاین کوئری =======
@bot.inline_handler(lambda query: True)
def inline_query_handler(inline_query):
    results = []
    for name, info in songs.items():
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

# ======= شروع ربات =======
bot.infinity_polling()
