import telebot
from telebot import types
import sqlite3

TOKEN = "8392429863:AAG9dVG4s3PrDj1aQltjRiuhFenb-hc8ZM8"

bot = telebot.TeleBot(TOKEN)

# Database
conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    invited_by INTEGER
)
""")

conn.commit()


# START
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        invited_by = None

        # نظام الدعوة
        if len(args) > 1:
            invited_by = int(args[1])
            if invited_by != user_id:
                cursor.execute("UPDATE users SET points = points + 700 WHERE user_id=?", (invited_by,))

        cursor.execute("INSERT INTO users (user_id, points, invited_by) VALUES (?, ?, ?)",
                       (user_id, 0, invited_by))
        conn.commit()

    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    points = cursor.fetchone()[0]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💎 تجميع نقاط", "👤 حسابي")
    markup.row("👥 رابط الدعوة", "♻️ تحويل نقاط")
    markup.row("🎟 استخدام كود")

    bot.send_message(message.chat.id,
f"""🔥 مرحبا بك في بوت النقاط 🔥

🆔 ID: {user_id}
💎 نقاطك: {points}

🎁 كل شخص يسجل عبر رابطك يمنحك 700 نقطة
""", reply_markup=markup)


# تجميع نقاط
@bot.message_handler(func=lambda m: m.text == "💎 تجميع نقاط")
def collect(m):
    user_id = m.from_user.id
    cursor.execute("UPDATE users SET points = points + 10 WHERE user_id=?", (user_id,))
    conn.commit()
    bot.send_message(m.chat.id, "✅ تحصلت على 10 نقاط 💎")


# حسابي
@bot.message_handler(func=lambda m: m.text == "👤 حسابي")
def account(m):
    user_id = m.from_user.id
    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    points = cursor.fetchone()[0]

    bot.send_message(m.chat.id,
f"""👤 حسابك

🆔 ID: {user_id}
💎 نقاطك: {points}
""")


# رابط الدعوة
@bot.message_handler(func=lambda m: m.text == "👥 رابط الدعوة")
def invite(m):
    user_id = m.from_user.id
    username = bot.get_me().username

    bot.send_message(m.chat.id,
f"""🔗 رابط الدعوة الخاص بك:
https://t.me/{username}?start={user_id}

🎁 كل شخص يسجل عبر رابطك يمنحك 700 نقطة
""")


# تحويل نقاط
@bot.message_handler(func=lambda m: m.text == "♻️ تحويل نقاط")
def transfer_start(m):
    msg = bot.send_message(m.chat.id, "📥 أرسل ID الشخص:")
    bot.register_next_step_handler(msg, get_transfer_id)


def get_transfer_id(m):
    receiver_id = int(m.text)
    msg = bot.send_message(m.chat.id, "💰 أرسل عدد النقاط:")
    bot.register_next_step_handler(msg, process_transfer, receiver_id)


def process_transfer(m, receiver_id):
    sender_id = m.from_user.id
    amount = int(m.text)

    cursor.execute("SELECT points FROM users WHERE user_id=?", (sender_id,))
    sender_points = cursor.fetchone()[0]

    if sender_points >= amount:
        cursor.execute("UPDATE users SET points = points - ? WHERE user_id=?", (amount, sender_id))
        cursor.execute("UPDATE users SET points = points + ? WHERE user_id=?", (amount, receiver_id))
        conn.commit()
        bot.send_message(m.chat.id, "✅ تم التحويل بنجاح")
    else:
        bot.send_message(m.chat.id, "❌ نقاطك غير كافية")


# استخدام كود بسيط (كود = FREE100)
@bot.message_handler(func=lambda m: m.text == "🎟 استخدام كود")
def code(m):
    msg = bot.send_message(m.chat.id, "📥 أرسل الكود:")
    bot.register_next_step_handler(msg, check_code)


def check_code(m):
    user_id = m.from_user.id
    if m.text == "FREE100":
        cursor.execute("UPDATE users SET points = points + 100 WHERE user_id=?", (user_id,))
        conn.commit()
        bot.send_message(m.chat.id, "🎉 تم إضافة 100 نقطة")
    else:
        bot.send_message(m.chat.id, "❌ الكود غير صحيح")


print("Bot is running...")
bot.infinity_polling()
