import telebot
from telebot import types

TOKEN = "8780687512:AAEznDGiwZDKdelnTV9LbRhKLR2KITML-zg"  # حط التوكن تاعك
CHANNEL_ID = -1003502571913    # ID القناة

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
    user_state[message.chat.id] = message.text
    bot.send_message(message.chat.id,
                     "✍️ اكتب تفاصيل الإعلان الآن:\nمثال:\nنوع الحساب:\nالسعر:")

@bot.message_handler(func=lambda message: message.chat.id in user_state)
def publish_ad(message):
    ad_type = user_state[message.chat.id]
    user = message.from_user

    # تحديد الاسم المعروض
    if user.username:
        display_name = f"@{user.username}"
    else:
        display_name = f"{user.first_name} {user.last_name if user.last_name else ''}".strip()

    text = f"""
🔥 إعلان جديد 🔥

📌 النوع: {ad_type}
👤 الناشر: {display_name}
🆔 ID: {user.id}

📝 التفاصيل:
{message.text}

⚠️ الإدارة غير مسؤولة عن أي تعامل خارج البوت.
"""

    # إنشاء أزرار Inline
    inline_buttons = types.InlineKeyboardMarkup(row_width=2)
    
    # زر التواصل مع البائع
    inline_buttons.add(types.InlineKeyboardButton(
        text="💬 تواصل مع البائع",
        url=f"tg://user?id={user.id}"
    ))

    # أزرار لكل نوع حساب/خدمة
    inline_buttons.add(
        types.InlineKeyboardButton("🎮 Free Fire", callback_data="freefire"),
        types.InlineKeyboardButton("🔫 PUBG", callback_data="pubg"),
        types.InlineKeyboardButton("⚽ FIFA", callback_data="fifa"),
        types.InlineKeyboardButton("📘 Facebook", callback_data="facebook"),
        types.InlineKeyboardButton("📸 Instagram", callback_data="instagram"),
        types.InlineKeyboardButton("🎵 TikTok", callback_data="tiktok"),
        types.InlineKeyboardButton("▶️ YouTube", callback_data="youtube")
    )

    # إرسال الإعلان مع الأزرار للقناة
    bot.send_message(CHANNEL_ID, text, reply_markup=inline_buttons)
    bot.send_message(message.chat.id, "✅ تم نشر إعلانك بنجاح في القناة!")
    del user_state[message.chat.id]

# التعامل مع الضغط على أزرار النوع
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # نقدر هنا نحط ردود بسيطة أو نرسل رسالة
    bot.answer_callback_query(call.id, f"🔹 لقد ضغطت على {call.data}")

print("Bot is running...")
bot.infinity_polling()
