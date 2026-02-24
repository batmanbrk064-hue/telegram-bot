import telebot
from telebot import types

TOKEN = "8780687512:AAEznDGiwZDKdelnTV9LbRhKLR2KITML-zg"
CHANNEL_ID = -1003502571913

bot = telebot.TeleBot(TOKEN)
user_state = {}

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📢 نشر إعلان بيع")
    markup.add("🔎 نشر طلب شراء")
    bot.send_message(message.chat.id,
                     "مرحبا بك في سوق NovaPoints 💎\nاختر الخدمة:",
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text in ["📢 نشر إعلان بيع", "🔎 نشر طلب شراء"])
def ask_details(message):
    user_state[message.chat.id] = {
        "type": message.text,
        "photos": []
    }
    bot.send_message(message.chat.id,
                     "✍️ اكتب تفاصيل الإعلان:")

# استقبال الصور
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.chat.id in user_state:
        file_id = message.photo[-1].file_id
        user_state[message.chat.id]["photos"].append(file_id)
        bot.send_message(message.chat.id,
                         "📸 تم حفظ الصورة.\nارسل صور أخرى أو اكتب /done للنشر.")

# عند الانتهاء
@bot.message_handler(commands=['done'])
def publish_ad(message):
    if message.chat.id not in user_state:
        return

    data = user_state[message.chat.id]
    user = message.from_user

    if user.username:
        display_name = f"@{user.username}"
    else:
        display_name = user.first_name

    text = f"""
🔥 إعلان جديد 🔥

📌 النوع: {data['type']}
👤 الناشر: {display_name}
🆔 ID: {user.id}

⚠️ الإدارة غير مسؤولة عن أي تعامل خارج البوت.
"""

    # زر تواصل فقط
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton(
        "💬 تواصل مع البائع",
        url=f"tg://user?id={user.id}"
    ))

    # إذا عندو صور
    if data["photos"]:
        media = []
        for photo in data["photos"]:
            media.append(types.InputMediaPhoto(photo))
        media[0].caption = text
        bot.send_media_group(CHANNEL_ID, media)
        bot.send_message(CHANNEL_ID, "اضغط للتواصل 👇", reply_markup=markup)
    else:
        bot.send_message(CHANNEL_ID, text, reply_markup=markup)

    bot.send_message(message.chat.id, "✅ تم نشر إعلانك بنجاح!")
    del user_state[message.chat.id]

# استقبال تفاصيل نصية
@bot.message_handler(func=lambda message: message.chat.id in user_state)
def save_text(message):
    user_state[message.chat.id]["details"] = message.text
    bot.send_message(message.chat.id,
                     "📸 إذا عندك صور ارسلهم الآن.\nللنشر بدون صور اكتب /done")

print("Bot is running...")
bot.infinity_polling()
