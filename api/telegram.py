import telebot
from telebot import types
import json
import os
from flask import Flask
import threading

TOKEN = "5548149661:AAFblu4NL86utR9SbzuE6RQ27HuD3Uiynas"
bot = telebot.TeleBot(TOKEN)

SONGS_FILE = "songs.json"
USERS_FILE = "users.json"
MY_ID = 5382282676  # فقط این آی‌دی می‌تواند آهنگ‌ها را حذف کند

# ===== Flask برای /ping =====
app = Flask(__name__)

@app.route("/ping")
def ping():
    return "pong", 200

# ===== بارگذاری آهنگ‌ها =====
if os.path.exists(SONGS_FILE):
    with open(SONGS_FILE, "r", encoding="utf-8") as f:
        songs = json.load(f)
else:
    songs = {
        "معین - آرزو داشتم": {"file": "https://t.me/solfg0_filebot/20", "thumb": "https://i.ibb.co/TMJLFKHZ/IMG-20251026-000741-631.jpg"},
        "معین - کعبه": {"file": "https://t.me/solfg0_filebot/23", "thumb": "https://i.ibb.co/KTLVWDk/IMG-20251026-032304-853.jpg"},
        "معین - مست": {"file": "https://t.me/solfg0_filebot/25", "thumb": "https://i.ibb.co/Hp36wWKT/images.jpg"},
        "معین - قسم به عشقمون": {"file": "https://t.me/solfg0_filebot/46", "thumb": "https://i.ibb.co/PsCdG52g/images-1.jpg"},
        "معین - طناز": {"file": "https://t.me/solfg0_filebot/49", "thumb": "https://i.ibb.co/ccs62YZp/images.jpg"},
        "معین - وقتی که تو رفتی": {"file": "https://t.me/solfg0_filebot/53", "thumb": "https://i.ibb.co/prnk7QHn/images-1.jpg"},
        "معین - من باهاتم": {"file": "https://t.me/solfg0_filebot/55", "thumb": "https://i.ibb.co/HDt4JXSV/images-2.jpg"},
        "معین - دعای شب": {"file": "https://t.me/solfg0_filebot/60", "thumb": "https://i.ibb.co/gM4K5rtg/images-3.jpg"},
        "معین - از راه اومدم": {"file": "https://t.me/solfg0_filebot/68", "thumb": "https://i.ibb.co/TDW3bhPN/images-1.jpg"},
        "معین - پروردگار": {"file": "https://t.me/solfg0_filebot/70", "thumb": "https://i.ibb.co/KzhXDh8B/images.jpg"}
    }

# ===== بارگذاری کاربران =====
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
else:
    users = []

# ===== توابع شمارش =====
def get_songs_count():
    return len(songs)

def get_users_count():
    return len(users)

# ===== آینلاین با مارک ربات =====
@bot.inline_handler(lambda query: True)
def inline_query_handler(inline_query):
    query_text = inline_query.query.lower()
    offset = int(inline_query.offset) if inline_query.offset else 0
    results = []

    filtered_songs = [(name, info) for name, info in songs.items() if query_text in name.lower() or query_text == ""]
    PAGE_SIZE = 50

    for name, info in filtered_songs[offset:offset + PAGE_SIZE]:
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="باز کردن در ربات", switch_inline_query_current_chat=name)
        markup.add(btn)
        results.append(types.InlineQueryResultArticle(
            id=name,
            title=name,
            description="کلیک کنید برای دریافت آهنگ",
            input_message_content=types.InputTextMessageContent(message_text=f"{name}\n{info['file']}"),
            thumbnail_url=info['thumb'],
            reply_markup=markup
        ))

    next_offset = str(offset + PAGE_SIZE) if offset + PAGE_SIZE < len(filtered_songs) else ""

    bot.answer_inline_query(
        inline_query.id,
        results,
        cache_time=0,
        is_personal=True,
        next_offset=next_offset,
        switch_pm_text="🔙 بازگشت به ربات 🇸‌🇴‌🇱‌🇫‌🇬‌0⃣🇧‌🇴‌🇹‌",
        switch_pm_parameter="start"
    )

# ===== صفحه‌بندی دکمه‌ها با حذف =====
def send_paginated_buttons(chat_id, song_list, page=0, per_page=10):
    start = page * per_page
    end = start + per_page
    markup = types.InlineKeyboardMarkup(row_width=2)

    for name in song_list[start:end]:
        btn_song = types.InlineKeyboardButton(text=name, callback_data=name)
        if chat_id == MY_ID:
            btn_delete = types.InlineKeyboardButton(text="🗑️", callback_data=f"delete_{name}")
            markup.add(btn_song, btn_delete)
        else:
            markup.add(btn_song)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(types.InlineKeyboardButton(text="⬅️ قبل", callback_data=f"page_{page-1}"))
    if end < len(song_list):
        nav_buttons.append(types.InlineKeyboardButton(text="بعد ➡️", callback_data=f"page_{page+1}"))
    if nav_buttons:
        markup.add(*nav_buttons)

    bot.send_message(chat_id, "نتایج جستجو:", reply_markup=markup)

# ===== استارت ربات =====
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id

    if chat_id not in users:
        users.append(chat_id)
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)

    markup = types.InlineKeyboardMarkup()
    count_btn = types.InlineKeyboardButton(text=f"تعداد ترانه‌ها: {get_songs_count()}", callback_data="count")
    users_btn = types.InlineKeyboardButton(text=f"تعداد کاربران: {get_users_count()}", callback_data="users_count")
    search_btn = types.InlineKeyboardButton(text="جستجو آهنگ‌ها", switch_inline_query_current_chat="")
    markup.add(count_btn, users_btn, search_btn)

    bot.send_message(chat_id, "سلام! برای پیدا کردن آهنگ‌ها روی دکمه زیر بزنید:", reply_markup=markup)

# ===== جستجو و اضافه کردن آهنگ =====
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()
    if '|' in text:
        parts = [p.strip() for p in text.split('|')]
        if len(parts) == 3:
            name, file_link, thumb_link = parts
            songs[name] = {"file": file_link, "thumb": thumb_link}
            with open(SONGS_FILE, "w", encoding="utf-8") as f:
                json.dump(songs, f, ensure_ascii=False, indent=4)
            bot.send_message(message.chat.id, f"🎵 آهنگ '{name}' با موفقیت اضافه شد.")
            return
        else:
            bot.send_message(message.chat.id, "فرمت اشتباه است، لطفاً دوباره تلاش کنید.")
            return

    query_words = text.lower().split()
    found_songs = {name: info for name, info in songs.items() if all(word in name.lower() for word in query_words)}
    if found_songs:
        song_list = list(found_songs.keys())
        send_paginated_buttons(message.chat.id, song_list)
    else:
        bot.send_message(message.chat.id, "هیچ نتیجه‌ای پیدا نشد.")

# ===== دکمه‌های شیشه‌ای و حذف =====
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data
    chat_id = call.message.chat.id

    if data == "count":
        bot.answer_callback_query(call.id, text=f"تعداد کل ترانه‌ها: {get_songs_count()}", show_alert=True)
        return
    if data == "users_count":
        bot.answer_callback_query(call.id, text=f"تعداد کاربران: {get_users_count()}", show_alert=True)
        return
    if data.startswith("page_"):
        page = int(data.split("_")[1])
        song_list = list(songs.keys())
        send_paginated_buttons(chat_id, song_list, page)
        return
    if data.startswith("delete_"):
        song_to_delete = data.split("_", 1)[1]
        if chat_id == MY_ID and song_to_delete in songs:
            del songs[song_to_delete]
            with open(SONGS_FILE, "w", encoding="utf-8") as f:
                json.dump(songs, f, ensure_ascii=False, indent=4)
            bot.answer_callback_query(call.id, text=f"آهنگ '{song_to_delete}' حذف شد.")
            song_list = list(songs.keys())
            send_paginated_buttons(chat_id, song_list)
        return
    if data in songs:
        info = songs[data]
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton(text="باز کردن در ربات", switch_inline_query_current_chat=data)
        markup.add(btn)
        bot.send_message(chat_id, f"{data}\n{info['file']}", reply_markup=markup)

# ===== اجرای همزمان Telebot و Flask =====
def run_telebot():
    bot.infinity_polling()

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

threading.Thread(target=run_telebot).start()
threading.Thread(target=run_flask).start()
