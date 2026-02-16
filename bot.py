import telebot
import random

TOKEN = "8133621209:AAFlNcROEdUavnNVnc5dz5bgt7SGuCkalkQ"

bot = telebot.TeleBot(TOKEN)

# ترحيب بالأعضاء الجدد في القروب
@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for user in message.new_chat_members:
        bot.send_message(
            message.chat.id,
            f"مرحبا بيك {user.first_name} 😍 نورت القروب، معاك عبدو بوت 😎"
        )

# الرد على الرسائل
@bot.message_handler(func=lambda message: True)
def reply(message):
    text = message.text.lower()

    # رد السلام
    if "سلام" in text or "السلام" in text:
        responses = [
            "وعليكم السلام ورحمة الله 🌸",
            "مرحبا خويا 😎",
            "ياهلا بيك 🤝"
        ]
        bot.reply_to(message, random.choice(responses))

    # رد كي يذكرو اسمك
    elif "عبدو" in text:
        responses = [
            "واش كاين؟ عبدو هنا 😎",
            "تنادي فيا؟ 👀",
            "أنا معاك خويا 🤝",
            "قول واش حاب 🔥"
        ]
        bot.reply_to(message, random.choice(responses))

    # ردود عامة
    else:
        responses = [
            "فهمتك 👍",
            "صح كلامك 😄",
            "هههه مليحة 🤣",
            "تمام 👌",
            "واش تحب نعاونك؟"
        ]
        bot.reply_to(message, random.choice(responses))

bot.infinity_polling()
