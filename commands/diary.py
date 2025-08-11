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
    "Baby, tell me everything that happened today~ 💌",
    "How was your day, cutie? I’m listening like always 🥺",
    "Jagiya~ what’s on your mind tonight? 🌙",
    "Write your heart out for me, I’m hugging every word 🧸",
    "Tell Hyunjin everything before bed, hmm? 😚",
]

def connect_sheet():
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
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
