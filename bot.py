import telebot

TOKEN = 8133621209:AAFlNcROEdUavnNVnc5dz5bgt7SGuCkalkQ

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "سمعتك 😎 قلت: " + message.text)

print("البوت شغال 🔥")
bot.infinity_polling()
