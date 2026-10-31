import telebot
import time
import os
import threading
from flask import Flask

# ----------------- Render Web Server -----------------

app = Flask('')

@app.route('/')
def home():
    return "Bot is live and running 24/7!"

def run_web():
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get("PORT", 10000)),
        use_reloader=False
    )

threading.Thread(target=run_web, daemon=True).start()

# ----------------- আপনার তথ্য -----------------

BOT_TOKEN = "8817776933:AAH9TIK11nizFApgyR3D4wafcc_xLQnQGQ4"
ADMIN_ID = 8864523429

bot = telebot.TeleBot(BOT_TOKEN)

USER_FILE = "users.txt"

# ----------------- আপনার Blogger Game URL -----------------

OPEN_URL = "https://freetaka12.blogspot.com/"

# ----------------- ইউজার সেভ -----------------

def save_user(user_id):
    users = set()

    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            users = set(f.read().splitlines())

    if str(user_id) not in users:
        with open(USER_FILE, "a") as f:
            f.write(f"{user_id}\n")

# ----------------- সব ইউজার পাওয়া -----------------

def get_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return [line.strip() for line in f if line.strip()]
    return []

# ----------------- START COMMAND WITH GIF -----------------

@bot.message_handler(commands=['start'])
def start(message):
    save_user(message.chat.id)

    keyboard = telebot.types.InlineKeyboardMarkup()

    open_button = telebot.types.InlineKeyboardButton(
        text="🌈✨ OPEN ✨🌈",
        web_app=telebot.types.WebAppInfo(url=OPEN_URL)
    )

    keyboard.add(open_button)

    welcome_text = (
        "👋 স্বাগতম!\n\n"
        "আমাদের এখানে কাজ করতে হলে "
        "নিচের OPEN বাটনে ক্লিক করুন। ❤️\n\n"
        "👇👇👇"
    )

    try:
        with open("start.gif", "rb") as gif:
            bot.send_animation(
                message.chat.id,
                gif,
                caption=welcome_text,
                reply_markup=keyboard
            )

    except Exception as e:
        print("GIF Error:", e)
        bot.send_message(
            message.chat.id,
            welcome_text,
            reply_markup=keyboard
        )

# ----------------- USER COUNT -----------------

@bot.message_handler(
    func=lambda message: message.text in ['/u', 'u', 'U', '/U']
)
def show_user_count(message):
    if message.chat.id != ADMIN_ID:
        return

    users = get_users()
    total_users = len(users)

    bot.reply_to(
        message,
        f"📊 বর্তমানে মোট ইউজার সংখ্যা: {total_users} জন"
    )

# ----------------- TEXT BROADCAST -----------------

@bot.message_handler(commands=['broadcast'])
def broadcast_text(message):
    if message.chat.id != ADMIN_ID:
        return

    text_to_send = message.text.replace('/broadcast', '', 1).strip()

    if not text_to_send:
        bot.reply_to(
            message,
            "⚠️ ব্রডকাস্টের জন্য টেক্সট লিখুন।\n"
            "উদাহরণ: /broadcast সবাই কেমন আছেন?"
        )
        return

    users = get_users()

    if not users:
        bot.reply_to(message, "❌ কোনো ইউজার পাওয়া যায়নি।")
        return

    status_msg = bot.reply_to(
        message,
        f"⏳ ব্রডকাস্ট শুরু হচ্ছে... মোট ইউজার: {len(users)}"
    )

    success, failed = 0, 0

    for u_id in users:
        try:
            bot.send_message(u_id, text_to_send)
            success += 1
            time.sleep(0.05)

        except Exception as e:
            failed += 1
            print("Broadcast Error:", e)

    bot.edit_message_text(
        f"✅ ব্রডকাস্ট সম্পন্ন!\n\n"
        f"🟢 সফল: {success}\n"
        f"🔴 ব্যর্থ: {failed}",
        chat_id=message.chat.id,
        message_id=status_msg.message_id
    )

# ----------------- PHOTO BROADCAST -----------------

@bot.message_handler(content_types=['photo'])
def broadcast_photo(message):
    if message.chat.id != ADMIN_ID:
        return

    caption = message.caption or ""

    if "/broadcast" in caption or caption == "":
        clean_caption = caption.replace('/broadcast', '').strip()
        photo_id = message.photo[-1].file_id

        users = get_users()

        if not users:
            bot.reply_to(message, "❌ কোনো ইউজার পাওয়া যায়নি।")
            return

        status_msg = bot.reply_to(
            message,
            f"⏳ ছবি ব্রডকাস্ট শুরু হচ্ছে... মোট ইউজার: {len(users)}"
        )

        success, failed = 0, 0

        for u_id in users:
            try:
                bot.send_photo(
                    u_id,
                    photo_id,
                    caption=clean_caption
                )
                success += 1
                time.sleep(0.05)

            except Exception as e:
                failed += 1
                print("Photo Error:", e)

        bot.edit_message_text(
            f"✅ ছবি ব্রডকাস্ট সম্পন্ন!\n\n"
            f"🟢 সফল: {success}\n"
            f"🔴 ব্যর্থ: {failed}",
            chat_id=message.chat.id,
            message_id=status_msg.message_id
        )

# ----------------- RUN BOT -----------------

print("Bot is running...")

bot.infinity_polling(
    timeout=20,
    long_polling_timeout=10
)
