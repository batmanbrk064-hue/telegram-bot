import telebot
import sqlite3
from telebot.types import ReplyKeyboardMarkup

TOKEN = "8392429863:AAG9dVG4s3PrDj1aQltjRiuhFenb-hc8ZM8"

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("database.db", check_same_thread=False)
cursor = conn.cursor()

# إنشاء الجداول
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    invited_by INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS codes (
    code TEXT PRIMARY KEY,
    value INTEGER
)
""")

conn.commit()

# ===== القائمة الرئيسية =====
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("💎 تجميع نقاط", "👤 حسابي")
    markup.row("👥 رابط الدعوة", "🔄 تحويل نقاط")
    markup.row("🎟 استخدام كود")
    return markup

# ===== تسجيل المستخدم =====
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    user = cursor.fetchone()

    if not user:
        invited_by = None
        if len(args) > 1:
            try:
                invited_by = int(args[1])
                cursor.execute("UPDATE users SET points = points + 700 WHERE user_id=?", (invited_by,))
            except:
                pass

        cursor.execute("INSERT INTO users (user_id, invited_by) VALUES (?,?)", (user_id, invited_by))
        conn.commit()

    bot.send_message(message.chat.id, "👋 مرحبا بك في بوت النقاط", reply_markup=main_menu())

# ===== الأزرار =====
@bot.message_handler(func=lambda m: True)
def handler(message):
    user_id = message.from_user.id

    if message.text == "💎 تجميع نقاط":
        cursor.execute("UPDATE users SET points = points + 10 WHERE user_id=?", (user_id,))
        conn.commit()
        bot.send_message(message.chat.id, "✅ تحصلت على 10 نقاط")

    elif message.text == "👤 حسابي":
        cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
        points = cursor.fetchone()[0]
        bot.send_message(message.chat.id, f"💰 نقاطك الحالية: {points}")

    elif message.text == "👥 رابط الدعوة":
        username = bot.get_me().username
        bot.send_message(
            message.chat.id,
            f"🔗 رابط الدعوة الخاص بك:\nhttps://t.me/{username}?start={user_id}\n\n🎁 كل شخص يسجل عبر رابطك يمنحك 700 نقطة!"
        )

    elif message.text == "🔄 تحويل نقاط":
        bot.send_message(message.chat.id, "✍️ اكتب بالشكل التالي:\nID عدد_النقاط\nمثال:\n123456789 50")

    elif message.text == "🎟 استخدام كود":
        bot.send_message(message.chat.id, "✍️ اكتب الكود الآن")

    else:
        parts = message.text.split()

        # تحويل نقاط
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            target = int(parts[0])
            amount = int(parts[1])

            cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
            sender_points = cursor.fetchone()[0]

            if sender_points >= amount:
                cursor.execute("UPDATE users SET points = points - ? WHERE user_id=?", (amount, user_id))
                cursor.execute("UPDATE users SET points = points + ? WHERE user_id=?", (amount, target))
                conn.commit()
                bot.send_message(message.chat.id, "✅ تم تحويل النقاط بنجاح")
            else:
                bot.send_message(message.chat.id, "❌ نقاطك غير كافية")

        else:
            # استعمال كود
            cursor.execute("SELECT value FROM codes WHERE code=?", (message.text,))
            code = cursor.fetchone()

            if code:
                cursor.execute("UPDATE users SET points = points + ? WHERE user_id=?", (code[0], user_id))
                cursor.execute("DELETE FROM codes WHERE code=?", (message.text,))
                conn.commit()
                bot.send_message(message.chat.id, f"🎉 مبروك! تحصلت على {code[0]} نقطة")
            else:
                pass

bot.polling()
