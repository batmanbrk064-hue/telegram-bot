import telebot

TOKEN = "8578519383:AAEkdS0dG8RXdaufR-bd5asqG3vmDQ4bcFo"
bot = telebot.TeleBot(TOKEN)

# اسمك لي يحب يسمعو البوت
MY_NAME = "عبدو"

# كلمات السلام
greetings = ["سلام", "اهلا", "مرحبا", "صباح الخير", "مساء الخير"]

@bot.message_handler(func=lambda message: True)
def reply(message):
    text = message.text.lower()
    user_name = message.from_user.first_name

    # اذا قال سلام
    if any(word in text for word in greetings):
        bot.reply_to(message, f"وعليكم السلام {user_name} 😊 كيفاش نعاونك اليوم؟")

    # اذا نادى اسمك
    elif MY_NAME.lower() in text:
        bot.reply_to(message, f"نعم سمعتك 😎 واش تحب يا {user_name}؟")

    # رد عادي كي انسان
    else:
        bot.reply_to(message, "فهمتك 👍 احكيلي أكثر...")
