import telebot
from telebot import types
import json, os, random
from datetime import datetime

TOKEN = "8392429863:AAG9dVG4s3PrDj1aQltjRiuhFenb-hc8ZM8"
ADMIN_ID = 123456789  



CHANNELS = ["@pizjzi", "@dksbsksk"]

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "data.json"

# تحميل البيانات
if os.path.exists(DATA_FILE):
    with open(DATA_FILE,"r") as f:
        users=json.load(f)
else:
    users={}

def save():
    with open(DATA_FILE,"w") as f:
        json.dump(users,f)

def level_calc(points):
    return points // 5000

def get_user(uid):
    uid=str(uid)
    if uid not in users:
        users[uid]={
            "points":500,
            "vip":False,
            "last_daily":"",
            "streak":0,
            "ref":None,
            "games_played":0
        }
        save()
    return users[uid]

def check_sub(uid):
    for ch in CHANNELS:
        try:
            member=bot.get_chat_member(ch,uid)
            if member.status not in ["member","administrator","creator"]:
                return False
        except:
            return False
    return True

def force_sub(msg):
    markup=types.InlineKeyboardMarkup()
    for ch in CHANNELS:
        markup.add(types.InlineKeyboardButton("📢 اشترك",url=f"https://t.me/{ch.replace('@','')}"))
    markup.add(types.InlineKeyboardButton("🔄 تحقق",callback_data="check"))
    bot.send_message(msg.chat.id,"🚫 اشترك في القنوات أولاً",reply_markup=markup)

def main_menu(msg):
    kb=types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("💰 حسابي","🎁 يومي")
    kb.add("🎰 سبين","🎮 ألعاب")
    kb.add("👑 VIP","🛒 متجر")
    kb.add("🏆 ترتيب","🔗 رابط الدعوة")
    bot.send_message(msg.chat.id,"💎 NovaPoints V10",reply_markup=kb)

@bot.message_handler(commands=['start'])
def start(msg):
    uid=msg.from_user.id
    args=msg.text.split()

    if not check_sub(uid):
        force_sub(msg)
        return

    user=get_user(uid)

    # نظام إحالة
    if len(args)>1:
        ref=args[1]
        if ref!=str(uid) and user["ref"] is None:
            user["ref"]=ref
            if ref in users:
                users[ref]["points"]+=1500
            save()

    main_menu(msg)

@bot.callback_query_handler(func=lambda c:c.data=="check")
def check_call(call):
    if check_sub(call.from_user.id):
        main_menu(call.message)
    else:
        bot.answer_callback_query(call.id,"❌ مازلت ما اشتركتش")

@bot.message_handler(func=lambda m:True)
def handler(msg):
    uid=msg.from_user.id
    if not check_sub(uid):
        force_sub(msg)
        return

    user=get_user(uid)

    if msg.text=="💰 حسابي":
        lvl=level_calc(user["points"])
        vip="🔥 VIP" if user["vip"] else "عادي"
        bot.send_message(msg.chat.id,
        f"💎 نقاطك: {user['points']}\n📊 Level: {lvl}\n👑 الحالة: {vip}")

    elif msg.text=="🎁 يومي":
        today=datetime.now().strftime("%Y-%m-%d")
        if user["last_daily"]==today:
            bot.send_message(msg.chat.id,"⏳ رجع غدوة")
        else:
            reward=2000 if user["vip"] else 1000
            user["points"]+=reward
            user["last_daily"]=today
            user["streak"]+=1
            save()
            bot.send_message(msg.chat.id,f"🔥 خذيت {reward} نقطة")

    elif msg.text=="🎰 سبين":
        reward=random.choice([0,500,1000,2000,5000])
        user["points"]+=reward
        save()
        bot.send_message(msg.chat.id,f"🎰 ربحت {reward}")

    elif msg.text=="🎮 ألعاب":
        game=random.choice(["guess","rps","box"])
        if game=="guess":
            num=random.randint(1,5)
            bot.send_message(msg.chat.id,f"🎯 خمنت الرقم {num} وربحت 1000")
            user["points"]+=1000
        elif game=="rps":
            bot.send_message(msg.chat.id,"✂️ حجر ورقة مقص - ربحت 800")
            user["points"]+=800
        else:
            reward=random.choice([0,1500,3000])
            bot.send_message(msg.chat.id,f"📦 صندوق الحظ: {reward}")
            user["points"]+=reward
        user["games_played"]+=1
        save()

    elif msg.text=="👑 VIP":
        if user["vip"]:
            bot.send_message(msg.chat.id,"🔥 انت VIP")
        elif user["points"]>=15000:
            user["points"]-=15000
            user["vip"]=True
            save()
            bot.send_message(msg.chat.id,"👑 تم تفعيل VIP")
        else:
            bot.send_message(msg.chat.id,"❌ تحتاج 15000 نقطة")

    elif msg.text=="🔗 رابط الدعوة":
        link=f"https://t.me/{bot.get_me().username}?start={uid}"
        bot.send_message(msg.chat.id,f"🔗 رابطك:\n{link}")

    elif msg.text=="🏆 ترتيب":
        top=sorted(users.items(),key=lambda x:x[1]["points"],reverse=True)[:10]
        text="🏆 Top 10:\n\n"
        for i,(u,d) in enumerate(top,1):
            text+=f"{i}- {d['points']} نقطة\n"
        bot.send_message(msg.chat.id,text)

    elif msg.text=="🛒 متجر":
        bot.send_message(msg.chat.id,"🛒 قريبا مزايا إضافية")

    elif uid==ADMIN_ID and msg.text=="/admin":
        bot.send_message(msg.chat.id,f"👑 عدد المستخدمين: {len(users)}")

bot.infinity_polling()
