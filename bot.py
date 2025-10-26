import telebot
from telebot import types

# 🔹 توکن رباتت
TOKEN = "توکن_ربات_تو_اینجا"
bot = telebot.TeleBot(TOKEN)

# ======= دکمه کشویی =======
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    # دکمه‌ای که پیام جدید با متن خاص می‌فرسته
    btn1 = types.InlineKeyboardButton(
        text="نمایش آهنگ‌ها",
        switch_inline_query_current_chat=""  # خالی یعنی جستجوی ربات فعال می‌شه
    )
    
    # دکمه‌ای که لینک باز می‌کنه
    btn2 = types.InlineKeyboardButton(
        text="باز کردن سایت",
        url="https://fa.telegram.org/"
    )
    
    markup.add(btn1, btn2)
    
    bot.send_message(
        message.chat.id,
        "سلام! از دکمه‌ها استفاده کن:",
        reply_markup=markup
    )

# ======= شروع ربات =======
bot.infinity_polling()
