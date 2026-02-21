import telebot
from telebot import types
import sqlite3
import random

TOKEN = "8392429863:AAG9dVG4s3PrDj1aQltjRiuhFenb-hc8ZM8"
ADMIN_ID = 7353077959
CHANNEL_USERNAME = "@dksbsksk"

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("data.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER,
    user_id INTEGER,
    service TEXT,
    status TEXT
)
""")

conn.commit()


# تحقق اشتراك
def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False


# START
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if not check_subscription(user_id):
        markup = types.InlineKeyboardMarkup()
        btn = types.InlineKeyboardButton("📢 اشترك في القناة", url="https://t.me/dksbsksk")
        markup.add(btn)
        bot.send_message(message.chat.id,
        "❌ لازم تشترك في القناة باش يخدم البوت",
        reply_markup=markup)
        return

    cursor.execute("INSERT OR IGNORE INTO users (user_id, points) VALUES (?, ?)", (user_id, 0))
    conn.commit()

    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    points = cursor.fetchone()[0]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row("📦 الخدمات")
    markup.row("💎 تجميع نقاط", "♻️ تحويل نقاط")
    markup.row("🎟 استخدام كود", "👤 الحساب")
    markup.row("🔍 فحص الطلب", "📨 طلباتي")
    markup.row("💰 شحن نقاط", "⚙️ تحديثات البوت")
    markup.row("📜 شروط الاستخدام")

    bot.send_message(message.chat.id,
f"""🔥 أهلا بك في بوت الخدمات 🔥

🆔 ايديك: {user_id}
💎 عدد نقاطك: {points}
""", reply_markup=markup)


# الخدمات
@bot.message_handler(func=lambda m: m.text == "📦 الخدمات")
def services(m):
    bot.send_message(m.chat.id,
"""📦 الخدمات:

1️⃣ 1000 متابع = 500 نقطة
2️⃣ 500 لايك = 300 نقطة
3️⃣ 1000 مشاهدة = 200 نقطة

✍️ اكتب رقم الخدمة لطلبها
""")


@bot.message_handler(func=lambda m: m.text in ["1", "2", "3"])
def order_service(m):
    user_id = m.from_user.id
    services = {
        "1": ("1000 متابع", 500),
        "2": ("500 لايك", 300),
        "3": ("1000 مشاهدة", 200)
    }

    service_name, price = services[m.text]

    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    points = cursor.fetchone()[0]

    if points < price:
        bot.send_message(m.chat.id, "❌ نقاطك غير كافية")
        return

    cursor.execute("UPDATE users SET points = points - ? WHERE user_id=?", (price, user_id))

    order_id = random.randint(10000, 99999)
    cursor.execute("INSERT INTO orders VALUES (?, ?, ?, ?)",
                   (order_id, user_id, service_name, "قيد المعالجة"))

    conn.commit()

    bot.send_message(m.chat.id, f"✅ تم إنشاء طلبك\n📦 الخدمة: {service_name}\n🆔 رقم الطلب: {order_id}")

    bot.send_message(ADMIN_ID,
    f"📨 طلب جديد\n🆔 {order_id}\n👤 {user_id}\n📦 {service_name}")


# طلباتي
@bot.message_handler(func=lambda m: m.text == "📨 طلباتي")
def my_orders(m):
    user_id = m.from_user.id
    cursor.execute("SELECT order_id, service, status FROM orders WHERE user_id=?", (user_id,))
    data = cursor.fetchall()

    if not data:
        bot.send_message(m.chat.id, "📭 لا توجد طلبات")
        return

    text = "📦 طلباتك:\n\n"
    for o in data:
        text += f"🆔 {o[0]} | {o[1]} | {o[2]}\n"

    bot.send_message(m.chat.id, text)


# تجميع
@bot.message_handler(func=lambda m: m.text == "💎 تجميع نقاط")
def collect(m):
    user_id = m.from_user.id
    cursor.execute("UPDATE users SET points = points + 15 WHERE user_id=?", (user_id,))
    conn.commit()
    bot.send_message(m.chat.id, "✅ تم إضافة 15 نقطة")


# الحساب
@bot.message_handler(func=lambda m: m.text == "👤 الحساب")
def account(m):
    user_id = m.from_user.id
    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    points = cursor.fetchone()[0]
    bot.send_message(m.chat.id, f"🆔 ID: {user_id}\n💎 نقاطك: {points}")


# كود
@bot.message_handler(func=lambda m: m.text == "🎟 استخدام كود")
def code(m):
    msg = bot.send_message(m.chat.id, "📥 أرسل الكود:")
    bot.register_next_step_handler(msg, check_code)


def check_code(m):
    if m.text == "FREE300":
        cursor.execute("UPDATE users SET points = points + 300 WHERE user_id=?", (m.from_user.id,))
        conn.commit()
        bot.send_message(m.chat.id, "🎉 تم إضافة 300 نقطة")
    else:
        bot.send_message(m.chat.id, "❌ الكود غير صحيح")


# شروط
@bot.message_handler(func=lambda m: m.text == "📜 شروط الاستخدام")
def rules(m):
    bot.send_message(m.chat.id, "📜 ممنوع السبام او الغش")


# تحديثات
@bot.message_handler(func=lambda m: m.text == "⚙️ تحديثات البوت")
def updates(m):
    bot.send_message(m.chat.id, "🆕 تم إطلاق نسخة احترافية")


# شحن
@bot.message_handler(func=lambda m: m.text == "💰 شحن نقاط")
def recharge(m):
    bot.send_message(m.chat.id, "💳 راسل الادمن بعد الدفع")


print("Bot Running...")
bot.infinity_polling()
