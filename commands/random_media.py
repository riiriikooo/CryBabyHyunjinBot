import os
import aiohttp
import random
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

# Read Tenor key from Replit Secrets
TENOR_KEY = os.environ.get("TENOR_API_KEY")
if not TENOR_KEY:
    raise RuntimeError("TENOR_API_KEY not found in environment")

# === API endpoints ===
CAT_API = "https://api.thecatapi.com/v1/images/search"
DOG_API = "https://dog.ceo/api/breeds/image/random"
FOX_API = "https://randomfox.ca/floof/"
MEME_API = "https://meme-api.com/gimme"
TENOR_API = "https://tenor.googleapis.com/v2/search"

async def fetch_json(url, params=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as resp:
            return await resp.json()

async def send_random_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = random.choice(["animal", "meme", "gif"])

    if choice == "animal":
        source = random.choice(["cat", "dog", "fox"])
        if source == "cat":
            data = await fetch_json(CAT_API)
            img_url = data[0]["url"]
        elif source == "dog":
            data = await fetch_json(DOG_API)
            img_url = data["message"]
        else:  # fox
            data = await fetch_json(FOX_API)
            img_url = data["image"]
        await update.message.reply_photo(img_url)

    elif choice == "meme":
        data = await fetch_json(MEME_API)
        img_url = data["url"]
        await update.message.reply_photo(img_url)

    elif choice == "gif":
        params = {
            "key": TENOR_KEY,
            "client_key": "CryBabyHyunjinBot",
            "q": "funny",
            "limit": 1,
            "random": "true"
        }
        data = await fetch_json(TENOR_API, params=params)
        if data.get("results"):
            gif_url = data["results"][0]["media_formats"]["gif"]["url"]
            await update.message.reply_animation(gif_url)
        else:
            await update.message.reply_text("Couldn't fetch a gif right now, try again!")

async def random_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        count = int(context.args[0]) if context.args else 1
    except ValueError:
        count = 1
    count = max(1, min(count, 10))  # limit between 1 and 10

    for _ in range(count):
        await send_random_media(update, context)

def get_random_media_handler():
    return CommandHandler("random", random_media)
