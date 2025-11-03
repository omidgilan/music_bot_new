# -*- coding: utf-8 -*-
import telebot
from telebot import types
import json
import os
import difflib
import re
from unidecode import unidecode

# ====== تنظیم توکن ======
TOKEN = "5548149661:AAEpk4ayC3UVyjQDmicXQFlWVKRy_6bdV88"  # <-- توکن خودت اینجاست
bot = telebot.TeleBot(TOKEN)

# ====== فایل‌ها ======
SONGS_FILE = "songs.json"
USERS_FILE = "users.json"
PLAYLISTS_FILE = "playlists.json"
TRASH_FILE = "trash.json"   # فایل سطل آشغال
MY_ID = 5382282676  # آی‌دی ادمین (سطل آشغال / حذف از دیتابیس)

# ===== توابع کمکی ======
def safe_load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, type(default)) else default
        except Exception:
            return default
    else:
        return default

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# بارگذاری امن اولیه
songs = safe_load_json(SONGS_FILE, {})
users = safe_load_json(USERS_FILE, [])
playlists = safe_load_json(PLAYLISTS_FILE, {})
trash = safe_load_json(TRASH_FILE, {})

# ===== جستجوی هوشمند =====
FUZZY_THRESHOLD = 0.25

def normalize_text(s):
    """
    نرمال‌سازی برای فارسی و انگلیسی:
    - lower
    - جایگزینی ی/ک عربی با فارسی
    - حذف حرکات و علائم کم‌اهمیت
    - حذف کاراکترهای غیرحرف/عدد به جز خط فاصله و underscore
    - حذف فاصله‌های اضافی و نیم‌فاصله
    """
    if not s:
        return ""
    s = str(s).lower().strip()
    s = s.replace("ي", "ی").replace("ك", "ک").replace("ـ", "")
    s = re.sub(r"[ًٌٍَُِّْٔʼ`´˝]", "", s)
    s = re.sub(r"[^\w\s\-]", " ", s)
    s = re.sub(r"[\u200c\s]+", " ", s)
    return s.strip()

def to_latin(s):
    """
    تبدیل به حروف لاتین بدون فاصله و کاراکترهای غیرحرفی
    برای مقایسهٔ فینگلیش/لاتین
    """
    if not s:
        return ""
    lat = unidecode(s).lower()
    lat = re.sub(r"[^a-z0-9]+", "", lat)
    return lat

def tokenize(s):
    """
    قطعه‌بندی رشته به توکن‌های معنادار (کلمات) بعد از نرمال‌سازی
    """
    s_norm = normalize_text(s)
    if not s_norm:
        return []
    return [tok for tok in re.split(r"\s+", s_norm) if tok]

def smart_search(query, dataset):
    """
    جستجوی هوشمند چند‌جانبه:
    - توکنایز کردن query و نام‌ها
    - مقایسه بر اساس:
        * substring در متن نرمال‌شده
        * substring در نسخه لاتین (برای فینگلیش)
        * fuzzy ratio کلی بین query و نام
    - امتیازدهی ترکیبی و فیلتر براساس آستانه
    - مرتب‌سازی بر اساس امتیاز نهایی
    """
    q_raw = query or ""
    q_norm = normalize_text(q_raw)
    q_lat = to_latin(q_raw)
    q_tokens = tokenize(q_raw)

    results = {}

    for name, info in dataset.items():
        name_norm = normalize_text(name)
        name_lat = to_latin(name)
        name_tokens = tokenize(name)

        score = 0.0
        max_token_score = 0.0

        # اگر کوئری خالی (مثلاً ".") یا نقطه بذارن، بر اساس fuzzy عمل می‌کنیم
        if q_norm == "." or q_norm == "":
            ratio = difflib.SequenceMatcher(None, q_norm, name_norm).ratio()
            ratio_lat = difflib.SequenceMatcher(None, q_lat, name_lat).ratio() if q_lat and name_lat else 0.0
            best_ratio = max(ratio, ratio_lat)
            if best_ratio >= FUZZY_THRESHOLD:
                score = best_ratio
            else:
                continue
            results[name] = (score, info)
            continue

        # توکن-به-توکن
        for qt in q_tokens:
            tok_score = 0.0
            if qt in name_norm:
                tok_score += 1.2
            if qt and qt == to_latin(qt) and qt in name_lat:
                tok_score += 1.5
            for nt in name_tokens:
                if nt.startswith(qt) or qt.startswith(nt):
                    tok_score += 0.6
            for nt in name_tokens:
                r = difflib.SequenceMatcher(None, qt, nt).ratio()
                if r > 0.6:
                    tok_score += r * 0.8
            if tok_score > max_token_score:
                max_token_score = tok_score
            score += tok_score

        # مقایسه کلی fuzzy
        overall_ratio = difflib.SequenceMatcher(None, q_norm, name_norm).ratio()
        overall_ratio_lat = 0.0
        if q_lat and name_lat:
            overall_ratio_lat = difflib.SequenceMatcher(None, q_lat, name_lat).ratio()
        best_overall = max(overall_ratio, overall_ratio_lat)
        score += best_overall * 1.5

        # پوشش توکن‌ها
        tokens_matched = 0
        for qt in q_tokens:
            if qt in name_norm or (qt and qt == to_latin(qt) and qt in name_lat):
                tokens_matched += 1
        if q_tokens:
            token_coverage = tokens_matched / len(q_tokens)
            score += token_coverage * 1.2

        # کوچک‌سازی برای نام‌های خیلی طولانی
        if len(name_norm.split()) > 6 and max_token_score < 0.8:
            score *= 0.8

        if score > 0.5 or best_overall >= FUZZY_THRESHOLD:
            results[name] = (score, info)

    sorted_items = sorted(
        results.items(),
        key=lambda kv: (kv[1][0], difflib.SequenceMatcher(None, q_norm, normalize_text(kv[0])).ratio()),
        reverse=True
    )

    return {name: info for (name, (score, info)) in sorted_items}

# ===== دکمه‌های ثابت زیر هر آهنگ =====
def get_song_buttons(song_name):
    markup = types.InlineKeyboardMarkup(row_width=2)
    btn_add = types.InlineKeyboardButton("➕", callback_data=f"add|{song_name}")
    btn_search = types.InlineKeyboardButton("🔍", switch_inline_query_current_chat=song_name)
    btn_delete_msg = types.InlineKeyboardButton("🗑️", callback_data=f"delmsg|{song_name}")
    btn_playlist = types.InlineKeyboardButton("🎧", switch_inline_query_current_chat="playlist_mode")
    markup.add(btn_add, btn_search)
    markup.add(btn_delete_msg, btn_playlist)
    return markup

# ===== ارسال آهنگ با دکمه‌ها =====
def send_song_with_buttons(chat_id, song_name, info, admin=False):
    markup = get_song_buttons(song_name)
    if admin:
        del_btn = types.InlineKeyboardButton("🗑️ حذف کامل", callback_data=f"deletedb|{song_name}")
        markup.add(del_btn)
    if isinstance(info, dict) and "file_id" in info:
        try:
            bot.send_audio(chat_id, audio=info["file_id"], caption=song_name, reply_markup=markup)
        except Exception:
            bot.send_message(chat_id, f"{song_name}\n(file_id:{info['file_id']})", reply_markup=markup)
    elif isinstance(info, dict) and "file" in info:
        bot.send_message(chat_id, f"{song_name}\n{info['file']}", reply_markup=markup)
    else:
        bot.send_message(chat_id, song_name, reply_markup=markup)

# ===== هندلر اینلاین =====
@bot.inline_handler(lambda q: True)
def inline_handler(inline_query):
    query = inline_query.query or "."
    user_key = str(inline_query.from_user.id)
    results = []

    if query == "playlist_mode":
        user_playlist = playlists.get(user_key, [])
        if not user_playlist:
            results.append(types.InlineQueryResultArticle(
                id="empty_playlist",
                title="پلی‌لیست خالی است 🎧",
                input_message_content=types.InputTextMessageContent("پلی‌لیست شما خالی است.")
            ))
        else:
            for i, entry in enumerate(user_playlist):
                title = entry.get("name", f"Track {i+1}")
                fid = entry.get("file_id")
                link = entry.get("file")
                safe_id = f"pl_{user_key}_{i}"
                if fid:
                    results.append(types.InlineQueryResultCachedAudio(
                        id=safe_id,
                        audio_file_id=fid,
                        caption=title,
                        reply_markup=get_song_buttons(title)
                    ))
                elif link:
                    results.append(types.InlineQueryResultAudio(
                        id=safe_id,
                        title=title,
                        audio_url=link,
                        performer="🎧 پلی‌لیست من",
                        reply_markup=get_song_buttons(title)
                    ))
    else:
        matches = list(smart_search(query, songs).items())[:50]
        for name, info in matches:
            safe_id = re.sub(r"[^0-9a-zA-Z_-]", "_", name)[:64]
            if isinstance(info, dict) and "file_id" in info:
                results.append(types.InlineQueryResultCachedAudio(
                    id=f"cached_{safe_id}",
                    audio_file_id=info["file_id"],
                    caption=name,
                    reply_markup=get_song_buttons(name)
                ))
            elif isinstance(info, dict) and "file" in info:
                results.append(types.InlineQueryResultAudio(
                    id=f"audio_{safe_id}",
                    title=name,
                    audio_url=info["file"],
                    performer="SOLFG BOT 🎵",
                    reply_markup=get_song_buttons(name)
                ))

    try:
        bot.answer_inline_query(
            inline_query.id,
            results,
            cache_time=0,
            is_personal=True,
            switch_pm_text="↩️ برگشت به ربات 🇸‌🇴‌🇱‌🇫‌🇬‌0⃣🇧‌🇴‌🇹‌ ↪️",
            switch_pm_parameter="start"
        )
    except Exception:
        pass

# ===== صفحه‌بندی نتایج جستجو =====
def send_paginated_buttons(chat_id, song_list, page=0, per_page=10):
    start = page * per_page
    end = start + per_page
    markup = types.InlineKeyboardMarkup(row_width=2)
    for name in song_list[start:end]:
        if chat_id == MY_ID:
            markup.add(types.InlineKeyboardButton(name, callback_data=name),
                       types.InlineKeyboardButton("🗑️", callback_data=f"delete_{name}"))
        else:
            markup.add(types.InlineKeyboardButton(name, callback_data=name))
    nav = []
    if page > 0:
        nav.append(types.InlineKeyboardButton("⬅️ قبل", callback_data=f"page_{page-1}"))
    if end < len(song_list):
        nav.append(types.InlineKeyboardButton("بعد ➡️", callback_data=f"page_{page+1}"))
    if nav:
        markup.add(*nav)
    bot.send_message(chat_id, "⬇️ نتایج جستجو ⬇️", reply_markup=markup)

# ===== استارت =====
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    if chat_id not in users:
        users.append(chat_id)
        save_json(USERS_FILE, users)
    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1 = types.InlineKeyboardButton(text=f"🎵 ترانه‌ها: {len(songs)}", callback_data="count_songs")
    btn2 = types.InlineKeyboardButton(text=f"👥 کاربران: {len(users)}", callback_data="count_users")
    btn3 = types.InlineKeyboardButton(text="🔍 جستجوی اینلاین", switch_inline_query_current_chat=".")
    btn_trash = types.InlineKeyboardButton(text="🗑️ سطل آشغال", callback_data="trash")
    markup.add(btn1, btn2, btn3)
    markup.add(btn_trash)
    bot.send_message(chat_id, "سلام! برای پیدا کردن آهنگ‌ها از گزینه‌های زیر استفاده کن:", reply_markup=markup)

# ===== ذخیره آهنگ از پیام صوتی =====
@bot.message_handler(content_types=['audio', 'voice'])
def save_audio(message):
    if message.audio:
        name = message.audio.title or f"Track {len(songs)+1}"
        songs[name] = {"file_id": message.audio.file_id}
        save_json(SONGS_FILE, songs)
        bot.reply_to(message, f"🎵 آهنگ '{name}' ذخیره شد ✅")

# ===== پیام‌های متنی و ذخیره لینک =====
@bot.message_handler(func=lambda message: message.text is not None)
def handle_text(message):
    text = message.text.strip()
    if "\n" in text:
        name, link = [p.strip() for p in text.split("\n", 1)]
        songs[name] = {"file": link}
        save_json(SONGS_FILE, songs)
        bot.send_message(message.chat.id, f"🎵 آهنگ '{name}' ذخیره شد.")
        return

    found = smart_search(text, songs)
    if found:
        send_paginated_buttons(message.chat.id, list(found.keys()))
    else:
        bot.send_message(message.chat.id, "❌ هیچ نتیجه‌ای یافت نشد. (فارسی یا فینگلیش رو امتحان کن)")

# ===== کال‌بک‌ها =====
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    data = call.data or ""
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    ukey = str(user_id)

    # آمارها
    if data == "count_songs":
        bot.answer_callback_query(call.id, text=f"🎵 تعداد آهنگ‌ها: {len(songs)}", show_alert=True)
        return
    if data == "count_users":
        bot.answer_callback_query(call.id, text=f"👥 تعداد کاربران: {len(users)}", show_alert=True)
        return

    # نمایش سطل آشغال
    if data == "trash":
        trash_list = list(trash.keys())
        if not trash_list:
            bot.answer_callback_query(call.id, text="🗑️ سطل آشغال خالی است", show_alert=True)
            return
        markup = types.InlineKeyboardMarkup(row_width=2)
        for name in trash_list:
            markup.add(types.InlineKeyboardButton(name, callback_data=f"trash_restore|{name}"),
                       types.InlineKeyboardButton("❌", callback_data=f"trash_delete|{name}"))
        bot.send_message(chat_id, "🗑️ سطل آشغال:", reply_markup=markup)
        bot.answer_callback_query(call.id, text="در حال نمایش سطل آشغال...", show_alert=False)
        return

    # بازیابی از سطل آشغال
    if data.startswith("trash_restore|"):
        if user_id != MY_ID:
            bot.answer_callback_query(call.id, text="فقط ادمین می‌تواند این کار را انجام دهد")
            return
        name = data.split("|",1)[1]
        if name in trash:
            songs[name] = trash.pop(name)
            save_json(SONGS_FILE, songs)
            save_json(TRASH_FILE, trash)
            bot.answer_callback_query(call.id, text=f"'{name}' بازیابی شد.")
        else:
            bot.answer_callback_query(call.id, text="آیتم در سطل آشغال یافت نشد.")
        return

    # حذف دائمی از سطل آشغال
    if data.startswith("trash_delete|"):
        if user_id != MY_ID:
            bot.answer_callback_query(call.id, text="فقط ادمین می‌تواند این کار را انجام دهد")
            return
        name = data.split("|",1)[1]
        if name in trash:
            trash.pop(name, None)
            save_json(TRASH_FILE, trash)
            bot.answer_callback_query(call.id, text=f"'{name}' به‌صورت دائمی حذف شد.")
        else:
            bot.answer_callback_query(call.id, text="آیتم در سطل آشغال یافت نشد.")
        return

    # صفحه‌بندی
    if data.startswith("page_"):
        page = int(data.split("_", 1)[1])
        send_paginated_buttons(chat_id, list(songs.keys()), page)
        return

    # حذف کامل از دیتابیس (سطل آشغال - ادمین) -> انتقال به trash
    if data.startswith("delete_"):
        if user_id != MY_ID:
            bot.answer_callback_query(call.id, text="فقط ادمین می‌تواند این کار را انجام دهد")
            return
        song = data.split("_", 1)[1]
        if song in songs:
            trash[song] = songs.pop(song)
            save_json(TRASH_FILE, trash)
            save_json(SONGS_FILE, songs)
            bot.answer_callback_query(call.id, text=f"'{song}' از دیتابیس حذف و به سطل آشغال منتقل شد.")
        else:
            bot.answer_callback_query(call.id, text="آهنگ یافت نشد.")
        return

    # حذف پیام جاری (local delete) - فقط ادمین می‌تواند پیام را حذف کند
    if data.startswith("delmsg|"):
        song = data.split("|", 1)[1]
        if user_id == MY_ID:
            try:
                bot.delete_message(chat_id, call.message.message_id)
                bot.answer_callback_query(call.id, text="پیام حذف شد")
            except Exception:
                bot.answer_callback_query(call.id, text="خطا در حذف پیام")
        else:
            bot.answer_callback_query(call.id, text="تنها ادمین می‌تواند این کار را انجام دهد")
        return

    # حذف کامل از دیتابیس از طریق دکمه admin روی پیام آهنگ -> انتقال به trash
    if data.startswith("deletedb|"):
        if user_id != MY_ID:
            bot.answer_callback_query(call.id, text="فقط ادمین می‌تواند این کار را انجام دهد")
            return
        song = data.split("|", 1)[1]
        if song in songs:
            trash[song] = songs.pop(song)
            save_json(TRASH_FILE, trash)
            save_json(SONGS_FILE, songs)
            bot.answer_callback_query(call.id, text="آهنگ از دیتابیس حذف و به سطل آشغال منتقل شد")
        else:
            bot.answer_callback_query(call.id, text="آهنگ یافت نشد")
        return

    # افزودن به پلی‌لیست کاربر
    if data.startswith("add|"):
        song = data.split("|", 1)[1]
        entry = {"name": song}
        # ضمیمه اطلاعات فایل در صورت وجود
        if song in songs:
            if "file_id" in songs[song]:
                entry["file_id"] = songs[song]["file_id"]
            elif "file" in songs[song]:
                entry["file"] = songs[song]["file"]
        user_playlist = playlists.get(ukey, [])
        if not any(x.get("name") == song for x in user_playlist):
            user_playlist.append(entry)
            playlists[ukey] = user_playlist
            save_json(PLAYLISTS_FILE, playlists)
            bot.answer_callback_query(call.id, text="🎶 آهنگ به پلی‌لیست شما اضافه شد")
        else:
            bot.answer_callback_query(call.id, text="ℹ️ این آهنگ قبلاً در پلی‌لیست وجود دارد")
        return

    # حذف از پلی‌لیست
    if data.startswith("remove_"):
        song = data.split("_", 1)[1]
        user_playlist = playlists.get(ukey, [])
        new_list = [item for item in user_playlist if item.get("name") != song]
        if len(new_list) != len(user_playlist):
            playlists[ukey] = new_list
            save_json(PLAYLISTS_FILE, playlists)
            bot.answer_callback_query(call.id, text="❌ آهنگ از پلی‌لیست حذف شد")
        else:
            bot.answer_callback_query(call.id, text="⚠️ این آهنگ در پلی‌لیست نبود")
        return

    # نمایش پلی‌لیست کاربر (ارسال هر آهنگ با دکمه‌ها)
    if data == "my_playlist":
        user_playlist = playlists.get(ukey, [])
        if not user_playlist:
            bot.answer_callback_query(call.id, text="پلی‌لیست شما خالیه 🎧", show_alert=True)
            return
        bot.answer_callback_query(call.id, text="📄 در حال ارسال پلی‌لیست...", show_alert=False)
        for entry in user_playlist:
            name = entry.get("name")
            # اگر نام در songs هست از آن استفاده کن، در غیر این صورت از دادهٔ entry
            if name in songs:
                send_song_with_buttons(chat_id, name, songs[name], admin=(user_id == MY_ID))
            else:
                info = {}
                if "file_id" in entry:
                    info["file_id"] = entry["file_id"]
                if "file" in entry:
                    info["file"] = entry["file"]
                send_song_with_buttons(chat_id, name, info, admin=(user_id == MY_ID))
        return

    # اگر کاربر روی نام آهنگ کلیک کرد (از صفحه نتایج)
    if data in songs:
        send_song_with_buttons(chat_id, data, songs[data], admin=(user_id == MY_ID))
        return

    # اگر هیچکدوم نبود، پیغام خطای پیش‌فرض
    bot.answer_callback_query(call.id, text="❌ عملیات نامشخص")

# ===== اجرای ربات =====
if __name__ == "__main__":
    print("ربات فعال شد ✅")
    bot.infinity_polling()
