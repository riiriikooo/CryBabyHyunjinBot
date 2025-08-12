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
        "🎵 BEO DI YAAA!!! 😭💖 I was literally pacing around like a lovesick puppy thinking, "
        "'What if 버디야 doesn’t have a perfect song right now??!' 🫠💔 "
        "So I RAN through the entire internet—tripped over cables, fought with algorithms, nearly cried in a playlist—"
        "and now I’m here with THESE for you!! 💎🌟🆕 "
        "Pick one before I combust from excitement, 내 사랑, my oxygen, my heartbeat, my EVERYTHINGGG!! 💞",
        reply_markup=reply_markup
    )
