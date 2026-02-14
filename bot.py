import requests
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import *

app = Client(
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


@app.on_message(filters.command("start"))
async def start_handler(client, message):
    user = message.from_user

    if not await check_join(client, user.id):
        return await message.reply(
            "🚨 You must join our channel to use this bot.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{FORCE_CHANNEL}")],
                [InlineKeyboardButton("✅ I Joined", callback_data="recheck")]
            ])
        )

    await message.reply_photo(
        photo="https://i.imgur.com/Zb8Q7tX.png",
        caption=f"""
🔥 **TeraBox Downloader Pro**

👋 Welcome {user.first_name}

📥 Send your TeraBox link and get direct download instantly!

⚡ Powered by xAPIVERSE
""",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 Send Link Now", switch_inline_query_current_chat="")]
        ])
    )


@app.on_callback_query()
async def callback_handler(client, callback_query):
    if callback_query.data == "recheck":
        if await check_join(client, callback_query.from_user.id):
            await callback_query.message.delete()
            await start_handler(client, callback_query.message)
        else:
            await callback_query.answer("❌ Still not joined!", show_alert=True)


@app.on_message(filters.text & filters.private)
async def download_handler(client, message):
    link = message.text.strip()

    if "terabox" not in link:
        return await message.reply("❌ Please send a valid TeraBox link.")

    msg = await message.reply("⏳ Fetching your file...")

    url = f"https://xapiverse.com/api/terabox-pro?apikey={XAPI_KEY}&url={link}"
    
    try:
        res = requests.get(url).json()

        if not res.get("status"):
            return await msg.edit("❌ Failed to fetch file.")

        file_name = res["data"]["file_name"]
        download_link = res["data"]["download_link"]

        await msg.edit(
            f"✅ **File Ready!**\n\n📁 {file_name}",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⬇ Download Now", url=download_link)]
            ])
        )

    except Exception as e:
        await msg.edit("⚠ API Error. Try again later.")


# Flask for Render healthcheck
from flask import Flask
import threading

web = Flask(__name__)

@web.route("/")
def home():
    return "Bot is running"

def run_web():
    web.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()

app.run()
