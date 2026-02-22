import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("8268898539:AAF6bykkUmzf40TyFlKurqOjoh7hjfjH25Q")

ADMIN_USERNAME = "@dksbsksk"  

keyboard = [
    ["🛒 نشر إعلان", "💰 طلب شراء"],
    ["📞 تواصل مع الإدارة"]
]

reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔥 مرحبا بك في DZ Market 🔥\n\nاختر من القائمة 👇",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🛒 نشر إعلان":
        await update.message.reply_text(
            "📌 ابعث تفاصيل الإعلان هكذا:\n\n"
            "• نوع الحساب\n"
            "• السعر\n"
            "• طريقة التواصل\n\n"
            "وسيتم مراجعته."
        )

    elif text == "💰 طلب شراء":
        await update.message.reply_text(
            "📩 اكتب اسم الحساب لي حاب تشريه\n"
            "وسيتم التواصل معك."
        )

    elif text == "📞 تواصل مع الإدارة":
        await update.message.reply_text(
            f"📞 تواصل مع الإدارة هنا:\n{ADMIN_USERNAME}"
        )

    else:
        await update.message.reply_text(
            "✅ تم استلام رسالتك.\n"
            "الإدارة تراجع الطلبات."
        )

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running...")
app.run_polling()
