import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = -1003502571913

keyboard = [
    ["🎮 Free Fire", "🎮 PUBG"],
    ["📘 Facebook", "🎵 TikTok"],
    ["📸 Instagram", "▶ YouTube"],
    ["📢 Telegram", "🛒 أخرى"]
]

reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 مرحبا بك في Market DZ 🔥\n\nاختر نوع الحساب لي حاب تبيع:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user = update.message.from_user

    categories = [
        "🎮 Free Fire", "🎮 PUBG",
        "📘 Facebook", "🎵 TikTok",
        "📸 Instagram", "▶ YouTube",
        "📢 Telegram", "🛒 أخرى"
    ]

    if text in categories:
        context.user_data["category"] = text
        await update.message.reply_text("ابعث تفاصيل الحساب (مستوى / متابعين / السعر) 💰")

    else:
        if "category" in context.user_data:
            category = context.user_data["category"]

            message = f"""
🔥 إعلان جديد 🔥

📌 النوع: {category}

📝 التفاصيل:
{text}

👤 البائع: @{user.username}
"""

            await context.bot.send_message(chat_id=CHANNEL_ID, text=message)

            await update.message.reply_text("✅ تم نشر إعلانك في القناة!")

            context.user_data.clear()
        else:
            await update.message.reply_text("اضغط /start باش تبدا")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot Running...")
    app.run_polling()
