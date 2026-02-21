import logging
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

TOKEN = "8392429863:AAG9dVG4s3PrDj1aQltjRiuhFenb-hc8ZM8"
CHANNEL_USERNAME = "@dksbsksk"

logging.basicConfig(level=logging.INFO)

conn = sqlite3.connect("nova.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    invited_by INTEGER,
    last_daily TEXT
)
""")
conn.commit()

# ----------- رتب -----------
def get_rank(points):
    if points >= 10000:
        return "💎 Diamond"
    elif points >= 5000:
        return "🥇 Gold"
    elif points >= 2000:
        return "🥈 Silver"
    else:
        return "🥉 Bronze"

# ----------- تحقق اشتراك -----------
async def is_subscribed(user_id, context):
    member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
    return member.status in ["member", "administrator", "creator"]

# ----------- START -----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id

    if not await is_subscribed(user_id, context):
        keyboard = [[InlineKeyboardButton("📢 اشترك في القناة", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")]]
        await update.message.reply_text(
            "❌ لازم تشترك في القناة باش يخدم البوت",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    ref = None
    if context.args:
        ref = int(context.args[0])

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (user_id, points, invited_by) VALUES (?, ?, ?)",
                       (user_id, 0, ref))
        conn.commit()
        if ref and ref != user_id:
            cursor.execute("UPDATE users SET points=points+700 WHERE user_id=?", (ref,))
            conn.commit()

    keyboard = [
        [InlineKeyboardButton("💰 نقاطي", callback_data="points")],
        [InlineKeyboardButton("🔗 رابط الدعوة", callback_data="ref")],
        [InlineKeyboardButton("🎁 مكافأة يومية", callback_data="daily")],
        [InlineKeyboardButton("🏆 المتصدرين", callback_data="top")]
    ]

    await update.message.reply_text(
        f"🔥 مرحبا بك في NovaPoints\nاختر من القائمة 👇",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ----------- أزرار -----------
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "points":
        cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
        points = cursor.fetchone()[0]
        rank = get_rank(points)
        await query.edit_message_text(f"💰 نقاطك: {points}\n🎖 رتبتك: {rank}")

    elif query.data == "ref":
        link = f"https://t.me/{context.bot.username}?start={user_id}"
        await query.edit_message_text(f"🔗 رابط الدعوة:\n{link}\n\n🎁 كل صديق = 700 نقطة")

    elif query.data == "daily":
        cursor.execute("SELECT last_daily FROM users WHERE user_id=?", (user_id,))
        data = cursor.fetchone()
        now = datetime.now()

        if data and data[0]:
            last = datetime.fromisoformat(data[0])
            if now - last < timedelta(hours=24):
                await query.edit_message_text("⏳ تقدر تاخذ المكافأة بعد 24 ساعة")
                return

        cursor.execute("UPDATE users SET points=points+500, last_daily=? WHERE user_id=?",
                       (now.isoformat(), user_id))
        conn.commit()
        await query.edit_message_text("🎉 ربحت 500 نقطة مكافأة يومية!")

    elif query.data == "top":
        cursor.execute("SELECT user_id, points FROM users ORDER BY points DESC LIMIT 10")
        top = cursor.fetchall()
        text = "🏆 أفضل 10 لاعبين:\n\n"
        for i, user in enumerate(top, start=1):
            text += f"{i}- ID {user[0]} | {user[1]} نقطة\n"
        await query.edit_message_text(text)

# ----------- تحويل نقاط -----------
async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if len(context.args) != 2:
        await update.message.reply_text("الصيغة:\n/transfer ID المبلغ")
        return

    target = int(context.args[0])
    amount = int(context.args[1])

    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    points = cursor.fetchone()[0]

    if amount <= 0 or points < amount:
        await update.message.reply_text("❌ نقاط غير كافية")
        return

    cursor.execute("SELECT * FROM users WHERE user_id=?", (target,))
    if not cursor.fetchone():
        await update.message.reply_text("❌ هذا المستخدم غير موجود")
        return

    cursor.execute("UPDATE users SET points=points-? WHERE user_id=?", (amount,user_id))
    cursor.execute("UPDATE users SET points=points+? WHERE user_id=?", (amount,target))
    conn.commit()

    await update.message.reply_text("✅ تم التحويل بنجاح")

# ----------- تشغيل -----------
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("transfer", transfer))
app.add_handler(CallbackQueryHandler(buttons))

print("NovaPoints V2 is running...")
app.run_polling()
