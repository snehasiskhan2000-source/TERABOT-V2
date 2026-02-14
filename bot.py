import os
import asyncio
import requests
from flask import Flask
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Environment variables
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
XAPI_KEY = os.getenv("XAPI_KEY")
FORCE_CHANNEL = os.getenv("FORCE_CHANNEL")

# Pyrogram app
bot = Client(
    "terabot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Force Join Check
async def check_join(client, user_id):
    try:
        await client.get_chat_member(FORCE_CHANNEL, user_id)
        return True
    except:
        return False


@bot.on_message(filters.command("start"))
async def start_handler(client, message):
    user = message.from_user

    if not await check_join(client, user.id):
        return await message.reply(
            "🚨 Join our channel to use this bot.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_CHANNEL}")]
            ])
        )

    await message.reply(
        f"🔥 Welcome {user.first_name}\n\nSend TeraBox link now!"
    )


@bot.on_message(filters.private & filters.text)
async def download_handler(client, message):
    link = message.text.strip()

    if "terabox" not in link:
        return await message.reply("❌ Send valid TeraBox link.")

    msg = await message.reply("⏳ Processing...")

    api_url = f"https://xapiverse.com/api/terabox-pro?apikey={XAPI_KEY}&url={link}"

    try:
        res = requests.get(api_url).json()

        if not res.get("status"):
            return await msg.edit("❌ Failed to fetch file.")

        file_name = res["data"]["file_name"]
        download_link = res["data"]["download_link"]

        await msg.edit(
            f"✅ File Ready\n\n📁 {file_name}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬇ Download", url=download_link)]
            ])
        )

    except:
        await msg.edit("⚠ API Error")


# Flask app (Render requires port binding)
web = Flask(__name__)

@web.route("/")
def home():
    return "Bot is running"

async def main():
    await bot.start()
    await bot.idle()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Run bot in background
    loop.create_task(main())

    # Run Flask on Render port
    web.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
