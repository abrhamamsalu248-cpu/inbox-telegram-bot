import os
import time
import html
import threading
from flask import Flask
import telebot

# Render ፖርት ፍተሻውን እንዲያልፍ የሚረዳ አጭር ሰርቨር
app = Flask(__name__)

@app.route('/')
def health_check():
    return "✅ Inbox Bot 24/7 እየሰራ ነው!"

BOT_TOKEN = os.environ.get("INBOX_BOT_TOKEN", "6822014973:AAGVZ8KJp3gj_gbLM80BE29orleubMIQ0XI")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "7105615214"))

bot = telebot.TeleBot(BOT_TOKEN)
message_tracker = {}

@bot.message_handler(commands=['start'])
def start_cmd(message):
    if message.chat.id == ADMIN_ID:
        bot.reply_to(message, "👑 ሰላም አድሚን! የ Inbox ቦትህ በ Render ላይ ዝግጁ ነው።")
    else:
        bot.reply_to(message, f"ሰላም {message.from_user.first_name}! 👋\nእንዴት ልንረዳዎ እንችላለን?")

@bot.message_handler(func=lambda msg: msg.chat.id != ADMIN_ID, content_types=['text', 'photo', 'voice', 'document', 'video', 'audio'])
def handle_incoming_user_message(message):
    user = message.from_user
    safe_name = html.escape(user.first_name or "User")
    safe_username = f"@{user.username}" if user.username else "No Username"
    user_info = f"👤 <b>ከ፦</b> {safe_name} ({safe_username})\n🆔 <b>ID፦</b> <code>{user.id}</code>"

    try:
        admin_msg = None
        if message.content_type == 'text':
            safe_text = html.escape(message.text)
            admin_msg = bot.send_message(ADMIN_ID, f"📩 <b>አዲስ መልእክት፦</b>\n{user_info}\n\n💬 {safe_text}", parse_mode="HTML")
        elif message.content_type == 'photo':
            caption = html.escape(message.caption or '')
            admin_msg = bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=f"📩 <b>አዲስ ፎቶ፦</b>\n{user_info}\n\n💬 {caption}", parse_mode="HTML")
        elif message.content_type == 'voice':
            admin_msg = bot.send_voice(ADMIN_ID, message.voice.file_id, caption=f"📩 <b>አዲስ ድምፅ፦</b>\n{user_info}", parse_mode="HTML")
        elif message.content_type == 'document':
            caption = html.escape(message.caption or '')
            admin_msg = bot.send_document(ADMIN_ID, message.document.file_id, caption=f"📩 <b>አዲስ ፋይል፦</b>\n{user_info}\n\n💬 {caption}", parse_mode="HTML")
        elif message.content_type == 'video':
            caption = html.escape(message.caption or '')
            admin_msg = bot.send_video(ADMIN_ID, message.video.file_id, caption=f"📩 <b>አዲስ ቪዲዮ፦</b>\n{user_info}\n\n💬 {caption}", parse_mode="HTML")

        if admin_msg:
            message_tracker[admin_msg.message_id] = user.id
    except Exception as e:
        print(f"Forward error: {e}")

@bot.message_handler(func=lambda msg: msg.chat.id == ADMIN_ID and msg.reply_to_message is not None, content_types=['text', 'photo', 'voice', 'document', 'video', 'audio'])
def handle_admin_direct_reply(message):
    original_msg_id = message.reply_to_message.message_id
    target_user_id = message_tracker.get(original_msg_id)

    if not target_user_id:
        bot.reply_to(message, "⚠️ የተጠቃሚው መረጃ አልተገኘም።")
        return

    try:
        if message.content_type == 'text':
            bot.send_message(target_user_id, message.text)
        elif message.content_type == 'photo':
            bot.send_photo(target_user_id, message.photo[-1].file_id, caption=message.caption or '')
        elif message.content_type == 'voice':
            bot.send_voice(target_user_id, message.voice.file_id)
        elif message.content_type == 'document':
            bot.send_document(target_user_id, message.document.file_id, caption=message.caption or '')
        elif message.content_type == 'video':
            bot.send_video(target_user_id, message.video.file_id, caption=message.caption or '')

        bot.reply_to(message, "✅ ተልኳል!")
    except Exception as e:
        bot.reply_to(message, f"❌ አልተላከም፦ {e}")

@bot.message_handler(commands=['reply'])
def handle_reply_cmd(message):
    if message.chat.id != ADMIN_ID:
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "⚠️ አጠቃቀም፦ `/reply <USER_ID> <መልእክት>`")
        return
    try:
        bot.send_message(int(parts[1]), parts[2])
        bot.reply_to(message, "✅ ተልኳል!")
    except Exception as e:
        bot.reply_to(message, f"❌ አልተላከም፦ {e}")

def run_bot_polling():
    try:
        bot.delete_webhook()
        time.sleep(1)
    except Exception as e:
        pass
    print("🚀 ቦቱ በ Render ላይ ስራ ጀምሯል...")
    bot.infinity_polling(skip_pending=True)

if __name__ == '__main__':
    # ቦቱን ከበስተጀርባ (Thread) ማስኬድ
    threading.Thread(target=run_bot_polling, daemon=True).start()
    
    # የ Render ፖርት ማስነሻ
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
