# -------- NovaPoints V4 PRO Game Edition --------

import sqlite3
from datetime import datetime, timedelta
from telegram import *
from telegram.ext import *

TOKEN = "8392429863:AAG9dVG4s3PrDj1aQltjRiuhFenb-hc8ZM8"
ADMIN_ID = 7353077959

conn = sqlite3.connect("nova_game.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    last_daily TEXT
)
""")

conn.commit()

# -------- الرتب --------
def get_rank(points):
    if points >= 20000:
        return "👑 Legend"
    elif points >= 10000:
        return "💎 Diamond"
    elif points >= 5000:
        return "🥇 Gold"
    elif points >= 2000:
        return "🥈 Silver"
    else:
        return "🥉 Bronze"

# -------- القائمة الرئيسية --------
def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 نقاطي", callback_data="points")],
        [InlineKeyboardButton("🎯 المهام", callback_data="tasks")],
        [InlineKeyboardButton("🛒 المتجر", callback_data="shop")],
        [InlineKeyboardButton("💳 السحب الداخلي", callback_data="withdraw")],
        [InlineKeyboardButton("🏆 المتصدرين", callback_data="top")],
        [InlineKeyboardButton("🎁 مكافأة يومية", callback_data="daily")]
    ])

def back():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 رجوع", callback_data="back")]])

# -------- START --------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    cursor.execute("INSERT OR IGNORE INTO users(user_id, points) VALUES (?,0)", (user_id,))
    conn.commit()
    await update.message.reply_text("🔥 مرحبا بك في NovaPoints Game", reply_markup=main_menu())

# -------- الأزرار --------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "points":
        cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
        pts = cursor.fetchone()[0]
        await query.edit_message_text(f"💰 نقاطك: {pts}\n🎖 رتبتك: {get_rank(pts)}", reply_markup=back())

    elif query.data == "daily":
        cursor.execute("SELECT last_daily FROM users WHERE user_id=?", (user_id,))
        data = cursor.fetchone()
        now = datetime.now()

        if data and data[0]:
            last = datetime.fromisoformat(data[0])
            if now - last < timedelta(hours=24):
                await query.edit_message_text("⏳ ارجع بعد 24 ساعة", reply_markup=back())
                return

        cursor.execute("UPDATE users SET points=points+500, last_daily=? WHERE user_id=?", (now.isoformat(), user_id))
        conn.commit()
        await query.edit_message_text("🎉 ربحت 500 نقطة!", reply_markup=back())

    elif query.data == "tasks":
        cursor.execute("UPDATE users SET points=points+300 WHERE user_id=?", (user_id,))
        conn.commit()
        await query.edit_message_text("✅ أكملت مهمة اليوم وربحت 300 نقطة!", reply_markup=back())

    elif query.data == "shop":
        await query.edit_message_text(
            "🛒 المتجر:\n\n"
            "1️⃣ 1000 نقطة = 2000 نقطة (Boost)\n"
            "2️⃣ ترقية رتبة بـ 5000 نقطة",
            reply_markup=back()
        )

    elif query.data == "withdraw":
        cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
        pts = cursor.fetchone()[0]

        if pts < 5000:
            await query.edit_message_text("❌ الحد الأدنى للسحب 5000 نقطة", reply_markup=back())
            return

        cursor.execute("UPDATE users SET points=points-5000 WHERE user_id=?", (user_id,))
        conn.commit()
        await query.edit_message_text("✅ تم خصم 5000 نقطة بنجاح!", reply_markup=back())

    elif query.data == "top":
        cursor.execute("SELECT user_id, points FROM users ORDER BY points DESC LIMIT 10")
        top = cursor.fetchall()
        text = "🏆 المتصدرين:\n\n"
        for i, u in enumerate(top, 1):
            text += f"{i}- {u[0]} | {u[1]} نقطة\n"
        await query.edit_message_text(text, reply_markup=back())

    elif query.data == "back":
        await query.edit_message_text("🔥 القائمة الرئيسية", reply_markup=main_menu())

# -------- لوحة الإدارة --------
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    await update.message.reply_text(f"👥 عدد المستخدمين: {count}")

# -------- تشغيل --------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CallbackQueryHandler(buttons))

print("NovaPoints V4 PRO Running...")
app.run_polling()
