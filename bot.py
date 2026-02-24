import telebot
from telebot import types

TOKEN = "8780687512:AAEznDGiwZDKdelnTV9LbRhKLR2KITML-zg" 
CHANNEL_ID = -1003502571913

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")
user_data = {}

# ===== START =====
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📢 نشر إعلان بيع", "🔎 نشر طلب شراء")
    bot.send_message(
        message.chat.id,
        "🔥 مرحبا بك في سوق NovaPoints 💎\n\nاختر نوع الإعلان:",
        reply_markup=markup
    )

# ===== اختيار النوع =====
@bot.message_handler(func=lambda m: m.text in ["📢 نشر إعلان بيع", "🔎 نشر طلب شراء"])
def choose_type(message):
    user_data[message.chat.id] = {
        "type": message.text,
        "details": "",
        "price": "",
        "photos": []
    }
    bot.send_message(message.chat.id, "✍️ اكتب تفاصيل الإعلان:")

# ===== حفظ التفاصيل =====
@bot.message_handler(func=lambda m: m.chat.id in user_data and user_data[m.chat.id]["details"] == "")
def get_details(message):
    user_data[message.chat.id]["details"] = message.text
    bot.send_message(message.chat.id, "💰 اكتب السعر فقط (مثال: 10$):")

# ===== حفظ السعر =====
@bot.message_handler(func=lambda m: m.chat.id in user_data and user_data[m.chat.id]["price"] == "")
def get_price(message):
    user_data[message.chat.id]["price"] = message.text
    bot.send_message(
        message.chat.id,
        "📸 ارسل صور المنتج (يمكن عدة صور).\n"
        "عند الانتهاء اكتب /done"
    )

# ===== استقبال الصور =====
@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    if message.chat.id in user_data:
        file_id = message.photo[-1].file_id
        user_data[message.chat.id]["photos"].append(file_id)
        bot.send_message(message.chat.id, "✅ تم حفظ الصورة.\nارسل أخرى أو /done للنشر.")

# ===== نشر الإعلان =====
@bot.message_handler(commands=['done'])
def publish(message):
    if message.chat.id not in user_data:
        return

    data = user_data[message.chat.id]
    user = message.from_user

    # اسم الناشر
    if user.username:
        name = f"@{user.username}"
    else:
        name = user.first_name

    caption = f"""
🔥 <b>إعلان جديد</b> 🔥

📌 <b>النوع:</b> {data['type']}
👤 <b>الناشر:</b> {name}
🆔 <b>ID:</b> <code>{user.id}</code>

📝 <b>التفاصيل:</b>
{data['details']}

💰 <b>السعر:</b> {data['price']}

⚠️ الإدارة غير مسؤولة عن أي تعامل خارج البوت.
"""

    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(
            "💬 تواصل مع البائع",
            url=f"tg://user?id={user.id}"
        )
    )

    # إذا فيه صور
    if data["photos"]:
        media = []
        for photo in data["photos"]:
            media.append(types.InputMediaPhoto(photo))

        media[0].caption = caption
        media[0].parse_mode = "HTML"

        bot.send_media_group(CHANNEL_ID, media)
        bot.send_message(CHANNEL_ID, "👇 للتواصل:", reply_markup=markup)
    else:
        bot.send_message(CHANNEL_ID, caption, reply_markup=markup)

    bot.send_message(message.chat.id, "✅ تم نشر إعلانك بنجاح!")
    del user_data[message.chat.id]

print("🚀 Bot is running...")
bot.infinity_polling()
