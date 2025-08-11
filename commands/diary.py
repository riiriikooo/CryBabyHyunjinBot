import os
import json
import random
import pytz
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, ConversationHandler, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Constants for Google Sheets
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "credentials.json"  # make sure this file is in your Replit project root
SHEET_NAME = "PAHyunjin_Diary"

WAITING_FOR_DIARY = 1

PROMPTS = [
    "Tell me everything that happened today~ 💌",
    "How was your day? I’m listening like always 🥺",
    "What wild chaos happened today? Tell Hyunjin everything, NOW! 😝💥",
    "Write, my sweetest! 🌸",
    "Words from you = magic! ✨",
    "Tell me your day in sparkles! ✨✨",
    "Tell me all the cute things! 🐰💕",
    "Your diary lights up my world! 💡✨",
    "Write~ and I’ll cherish it forever! 🥰💝",
    "Share a secret you’ve never told me! 🤫❤️",
    "What’s a funny thing that happened today? Make me laugh! 😂💕",
    "What’s something you’re grateful for today? I’m grateful for you! 🙏❤️",
    "Tell me one thing you want me to never forget about you! I’m all ears! 👂💖",
    "Tell me about a tiny moment that made you go “aww!” 🥺💕",
    "What’s a tiny act of kindness you noticed or did today? You’re my angel! 😇💕",
    "What’s something you want to remember forever? I’ll keep it safe! 🔒💝",
    "What’s a gentle reminder you want to give yourself right now? 💌💫",
]

def connect_sheet():
    creds_json = os.getenv("GOOGLE_CREDS_JSON")
    creds_dict = json.loads(creds_json)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1
    return sheet

async def diary_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    prompt = random.choice(PROMPTS)
    await update.message.reply_text(prompt)
    return WAITING_FOR_DIARY

async def diary_receive(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text
    tz = pytz.timezone("Asia/Singapore")
    now = datetime.now(tz)
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%I:%M %p")

    sheet = connect_sheet()
    sheet.append_row([date_str, time_str, text])

    await update.message.reply_text("Diary saved, my love 🥰💖")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Okay baby, talk later 🥺💕")
    return ConversationHandler.END

# You can also export the ConversationHandler here for easy import in main.py

def get_diary_handler():
    from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler

    diary_handler = ConversationHandler(
        entry_points=[CommandHandler("diary", diary_start)],
        states={
            WAITING_FOR_DIARY: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, diary_receive)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    return diary_handler
