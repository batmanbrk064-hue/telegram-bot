import telebot

TOKEN = "8133621209:AAFlNcROEdUavnNVnc5dz5bgt7SGuCkalkQ"

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def reply_all(message):
    bot.reply_to(message, "واش كاين 😎")

print("البوت راهو خدام 🔥")

bot.infinity_polling()
