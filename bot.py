import telebot
from telebot import types

TOKEN = "8780687512:AAEznDGiwZDKdelnTV9LbRhKLR2KITML-zg"
CHANNEL_ID = -1003502571913

bot = telebot.TeleBot(TOKEN)
user_state = {}

# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📢 نشر إعلان بيع", "🔎 نشر طلب شراء")
    bot.send_message(message.chat.id,
                     "مرحبا بك في سوق NovaPoints 💎\nاختر الخدمة:",
                     reply_markup=markup)

# ===== اختيار النوع =====
@bot.message_handler(func=lambda message: message.text in ["📢 نشر إعلان بيع", "🔎 نشر طلب شراء"])
def ask_details(message):
    user_state[message.chat.id] = {
        "type": message.text,
        "text": "",
        "photos": []
    }
    bot.send_message(message.chat.id,
                     "✍️ اكتب تفاصيل الإعلان أو أرسل الصور مباشرة.\n"
                     "عند الانتهاء اكتب /done")

# ===== حفظ النص =====
@bot.message_handler(func=lambda message: message.chat.id in user_state and message.content_type == "text" and message.text != "/done")
def save_text(message):
    user_state[message.chat.id]["text"] += message.text + "\n"

# ===== حفظ الصور =====
@bot.message_handler(content_types=['photo'])
def save_photo(message):
    if message.chat.id in user_state:
        file_id = message.photo[-1].file_id
        user_state[message.chat.id]["photos"].append(file_id)
        bot.send_message(message.chat.id,
                         "📸 تم حفظ الصورة.\nارسل أخرى أو /done للنشر.")

# ===== نشر الإعلان =====
@bot.message_handler(commands=['done'])
def publish_ad(message):
    if message.chat.id not in user_state:
        return

    data = user_state[message.chat.id]
    ad_type = data["type"]
    user = message.from_user

    if user.username:
        display_name = f"@{user.username}"
    else:
        display_name = user.first_name

    text = f"""
🔥 إعلان جديد 🔥

📌 النوع: {ad_type}
👤 الناشر: {display_name}
🆔 ID: {user.id}

📝 التفاصيل:
{data['text']}

⚠️ الإدارة غير مسؤولة عن أي تعامل خارج البوت.
"""

    markup = types.InlineKeyboardMarkup()

    if ad_type == "📢 نشر إعلان بيع":
        button_text = "💬 تواصل مع البائع"
    else:
        button_text = "💬 تواصل مع المشتري"

    markup.add(types.InlineKeyboardButton(
        text=button_text,
        url=f"tg://user?id={user.id}"
    ))

    # إذا كاين صور
    if data["photos"]:
        media = []
        for photo in data["photos"]:
            media.append(types.InputMediaPhoto(photo))

        media[0].caption = text
        bot.send_media_group(CHANNEL_ID, media)
        bot.send_message(CHANNEL_ID, "👇 للتواصل:", reply_markup=markup)
    else:
        bot.send_message(CHANNEL_ID, text, reply_markup=markup)

    bot.send_message(message.chat.id, "✅ تم نشر إعلانك بنجاح!")
    del user_state[message.chat.id]

print("Bot is running...")
bot.infinity_polling()
