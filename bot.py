import os
import requests
from flask import Flask
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 🔐 Environment Variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
XAPI_KEY = os.getenv("XAPI_KEY")
FORCE_CHANNEL = os.getenv("FORCE_CHANNEL")

# 🤖 Telegram App
app = ApplicationBuilder().token(BOT_TOKEN).build()

# 🔎 Force Join Check
async def check_join(user_id, context):
    try:
        member = await context.bot.get_chat_member(f"@{FORCE_CHANNEL}", user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


# 🚀 Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not await check_join(user.id, context):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_CHANNEL}")]
        ]
        await update.message.reply_text(
            "🚨 You must join our channel to use this bot.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        return

    await update.message.reply_text(
        f"🔥 *TeraBox Downloader Pro*\n\n"
        f"👋 Welcome {user.first_name}\n\n"
        f"📥 Send your TeraBox link now!",
        parse_mode="Markdown",
    )


# 📥 Download Handler
async def download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    link = update.message.text.strip()

    if "terabox" not in link.lower():
        await update.message.reply_text("❌ Please send a valid TeraBox link.")
        return

    msg = await update.message.reply_text("⏳ Processing your link...")

    api_url = f"https://xapiverse.com/api/terabox-pro?apikey={XAPI_KEY}&url={link}"

    try:
        res = requests.get(api_url).json()

        if not res.get("status"):
            await msg.edit_text("❌ Failed to fetch file.")
            return

        file_name = res["data"]["file_name"]
        download_link = res["data"]["download_link"]

        keyboard = [
            [InlineKeyboardButton("⬇ Download File", url=download_link)]
        ]

        await msg.edit_text(
            f"✅ *File Ready!*\n\n📁 {file_name}",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    except Exception as e:
        await msg.edit_text("⚠ API Error. Try again later.")


# 🔗 Add Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download))


# 🌐 Flask (Render Port Binding)
web = Flask(__name__)

@web.route("/")
def home():
    return "Bot is running!"

if __name__ == "__main__":
    import threading

    # Run bot in background thread
    threading.Thread(target=lambda: app.run_polling()).start()

    # Run Flask
    web.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
