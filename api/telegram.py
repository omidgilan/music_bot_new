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
    songs = {}

# ===== بارگذاری کاربران =====
if os.path.exists(USERS_FILE):
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
else:
    users = []

# ===== توابع ذخیره‌سازی =====
def save_songs():
    with open(SONGS_FILE, "w", encoding="utf-8") as f:
        json.dump(songs, f, ensure_ascii=False, indent=4)

def save_users():
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# ===== شمارش =====
def get_songs_count():
    return len(songs)

def get_users_count():
    return len(users)

# ===== Inline با مارک ربات =====
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

# ===== دکمه‌ها با صفحه‌بندی =====
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

# ===== استارت =====
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if chat_id not in users:
        users.append(chat_id)
        save_users()

    markup = types.InlineKeyboardMarkup()
    count_btn = types.InlineKeyboardButton(text=f"تعداد ترانه‌ها: {get_songs_count()}", callback_data="count")
    users_btn = types.InlineKeyboardButton(text=f"تعداد کاربران: {get_users_count()}", callback_data="users_count")
    search_btn = types.InlineKeyboardButton(text="جستجو آهنگ‌ها", switch_inline_query_current_chat="")
    markup.add(count_btn, users_btn, search_btn)

    bot.send_message(chat_id, "سلام! برای پیدا کردن آهنگ‌ها روی دکمه زیر بزنید:", reply_markup=markup)

# ===== جستجو و اضافه آهنگ =====
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()
    if '|' in text:
        parts = [p.strip() for p in text.split('|')]
        if len(parts) == 3:
            name, file_link, thumb_link = parts
            songs[name] = {"file": file_link, "thumb": thumb_link}
            save_songs()
            bot.send_message(message.chat.id, f"🎵 آهنگ '{name}' با موفقیت اضافه شد.")
            return
        else:
            bot.send_message(message.chat.id, "فرمت اشتباه است، لطفاً دوباره تلاش کنید.")
            return

    query_words = text.lower().split()
    found_songs = {name: info for name, info in songs.items() if all(word in name.lower() for word in query_words)}
    if found_songs:
        send_paginated_buttons(message.chat.id, list(found_songs.keys()))
    else:
        bot.send_message(message.chat.id, "هیچ نتیجه‌ای پیدا نشد.")

# ===== Callback دکمه‌ها =====
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
        send_paginated_buttons(chat_id, list(songs.keys()), page)
        return
    if data.startswith("delete_"):
        song_to_delete = data.split("_", 1)[1]
        if chat_id == MY_ID and song_to_delete in songs:
            del songs[song_to_delete]
            save_songs()
            bot.answer_callback_query(call.id, text=f"آهنگ '{song_to_delete}' حذف شد.")
            send_paginated_buttons(chat_id, list(songs.keys()))
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
