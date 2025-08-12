from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

async def song_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("💎 Hidden Gem", callback_data='song_hidden'),
            InlineKeyboardButton("🌟 Trending", callback_data='song_trending')
        ],
        [
            InlineKeyboardButton("🆕 New Release", callback_data='song_new')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎵 What do you want today, 버디야?",
        reply_markup=reply_markup
    )
