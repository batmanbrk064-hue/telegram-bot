import sqlite3
from telegram import *
from telegram.ext import *

TOKEN = "8392429863:AAG9dVG4s3PrDj1aQltjRiuhFenb-hc8ZM8"
CHANNEL_USERNAME = "@dksbsksk"
ADMIN_ID = 123456789
REF_POINTS = 700

conn = sqlite3.connect("novapoints.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, points INTEGER)")
cursor.execute("CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, service TEXT, status TEXT)")
cursor.execute("CREATE TABLE IF NOT EXISTS codes (code TEXT PRIMARY KEY, value INTEGER)")
conn.commit()

async def check_sub(user_id, bot):
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member","administrator","creator"]
    except:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await check_sub(user_id, context.bot):
        keyboard = [
            [InlineKeyboardButton("🔔 اشترك", url="https://t.me/dksbsksk")],
            [InlineKeyboardButton("✅ تحقق", callback_data="check")]
        ]
        await update.message.reply_text("⚠️ لازم تشترك باش يخدم NovaPoints",
                                        reply_markup=InlineKeyboardMarkup(keyboard))
        return

    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users VALUES (?, 0)", (user_id,))
        conn.commit()

    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    points = cursor.fetchone()[0]

    text = f"""
💎 NovaPoints 💎

👤 ID: `{user_id}`
💳 نقاطك: {points}

🎁 كل دعوة = {REF_POINTS} نقطة
"""

    keyboard = [
        [InlineKeyboardButton("📦 الخدمات", callback_data="services")],
        [InlineKeyboardButton("🎟 كود هدية", callback_data="gift")],
        [InlineKeyboardButton("📊 حسابي", callback_data="account")],
        [InlineKeyboardButton("💸 رابط الدعوة", callback_data="ref")]
    ]

    await update.message.reply_text(text, parse_mode="Markdown",
                                    reply_markup=InlineKeyboardMarkup(keyboard))

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "check":
        if await check_sub(user_id, context.bot):
            await query.answer("✅ تم التحقق", show_alert=True)
        else:
            await query.answer("❌ مازلت ما اشتركتش", show_alert=True)

    elif query.data == "services":
        keyboard = [
            [InlineKeyboardButton("📈 زيادة تفاعل (1000)", callback_data="rush")],
            [InlineKeyboardButton("🎮 شحن ألعاب (2000)", callback_data="games")],
            [InlineKeyboardButton("📢 نشر ممول (1500)", callback_data="promo")],
            [InlineKeyboardButton("🔙 رجوع", callback_data="back")]
        ]
        await query.message.edit_text("💎 اختر الخدمة:",
                                      reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "gift":
        await query.message.edit_text("✍️ اكتب:\n/code اسم_الكود")

    elif query.data in ["rush","games","promo"]:
        cost = 1000 if query.data=="rush" else 2000 if query.data=="games" else 1500

        cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
        points = cursor.fetchone()[0]

        if points >= cost:
            cursor.execute("UPDATE users SET points=points-? WHERE user_id=?", (cost,user_id))
            cursor.execute("INSERT INTO orders (user_id, service, status) VALUES (?,?,?)",
                           (user_id, query.data, "قيد المراجعة"))
            conn.commit()
            await query.message.edit_text("⏳ تم إرسال طلبك للإدارة")
        else:
            await query.answer("❌ نقاط غير كافية", show_alert=True)

    elif query.data == "account":
        cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
        points = cursor.fetchone()[0]
        await query.message.edit_text(f"👤 حسابك\n💳 نقاطك: {points}")

    elif query.data == "ref":
        bot_username = (await context.bot.get_me()).username
        link = f"https://t.me/{bot_username}?start={user_id}"
        await query.message.reply_text(f"🔗 رابطك:\n{link}")

    elif query.data == "back":
        await start(update, context)

# 🔥 تحويل نقاط
async def transfer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if len(context.args) != 2:
        await update.message.reply_text("❌ الصيغة:\n/transfer ID عدد_النقاط")
        return

    try:
        target_id = int(context.args[0])
        amount = int(context.args[1])
    except:
        await update.message.reply_text("❌ تأكد من كتابة ID و العدد صحيح")
        return

    if amount <= 0:
        await update.message.reply_text("❌ عدد نقاط غير صالح")
        return

    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    sender = cursor.fetchone()

    if not sender or sender[0] < amount:
        await update.message.reply_text("❌ نقاطك غير كافية")
        return

    cursor.execute("SELECT * FROM users WHERE user_id=?", (target_id,))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users VALUES (?, 0)", (target_id,))

    cursor.execute("UPDATE users SET points=points-? WHERE user_id=?", (amount,user_id))
    cursor.execute("UPDATE users SET points=points+? WHERE user_id=?", (amount,target_id))
    conn.commit()

    await update.message.reply_text(f"✅ تم تحويل {amount} نقطة بنجاح")

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("❌ اكتب اسم الكود")
        return

    code = context.args[0]
    cursor.execute("SELECT value FROM codes WHERE code=?", (code,))
    data = cursor.fetchone()

    if data:
        value = data[0]
        cursor.execute("UPDATE users SET points=points+? WHERE user_id=?", (value,user_id))
        cursor.execute("DELETE FROM codes WHERE code=?", (code,))
        conn.commit()
        await update.message.reply_text(f"🎉 تم إضافة {value} نقطة بنجاح!")
    else:
        await update.message.reply_text("❌ كود غير صالح")

async def create_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    try:
        code = context.args[0]
        value = int(context.args[1])
        cursor.execute("INSERT INTO codes VALUES (?,?)", (code,value))
        conn.commit()
        await update.message.reply_text(f"✅ تم إنشاء الكود {code} بقيمة {value} نقطة")
    except:
        await update.message.reply_text("❌ الصيغة:\n/createcode CODE 1000")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("code", redeem))
app.add_handler(CommandHandler("createcode", create_code))
app.add_handler(CommandHandler("transfer", transfer))
app.add_handler(CallbackQueryHandler(buttons))

print("NovaPoints Running...")
app.run_polling()
