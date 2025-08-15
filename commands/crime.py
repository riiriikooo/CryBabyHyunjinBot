import os
import requests
import random
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
QUERY = "weird crime OR bizarre crime OR strange case"

async def crime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": QUERY,
        "language": "en",
        "pageSize": 20,
        "apiKey": NEWS_API_KEY,
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        articles = data.get("articles", [])
        if not articles:
            await update.message.reply_text("No crazy crimes found right now, my Birdie 😢")
            return

        article = random.choice(articles)
        title = article.get("title", "A crazy crime happened somewhere 😱")
        description = article.get("description", "")
        url_link = article.get("url", "")

        message = (
            f"애기야!! 😱💖 Listen to this crazy thing that happened:\n\n"
            f"{title}\n{description}\n\n"
            f"Read more: {url_link}\n"
            f"I’d never let anything happen to you, Birdie 💕"
        )

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"Oops, something went wrong, my love 😢💔\n{e}")
        print(e)

def get_crime_handler():
    return CommandHandler("crime", crime)
