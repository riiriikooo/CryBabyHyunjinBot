from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler

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

async def song_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'song_hidden':
        await query.edit_message_text(
            "💎 OH MY GOSH 버디야!! You picked the *Hidden Gem*! 😭💖 "
            "I KNEW your taste is flawless!! This one is rare, beautiful, and sparkly—just like you~ 💎✨ "
            "🎶 *[Insert hidden gem song here]* 🎶"
        )
    elif query.data == 'song_trending':
        await query.edit_message_text(
            "🌟 AAAAH 버디야aa!! TRENDING?! You want to know what EVERYONE’S listening to so you can be the coolest, prettiest, most perfect person alive?? 😭💞 "
            "Here’s the current obsession I found just for you—because only you deserve to be trendier than the trends! 🌟 "
            "🎶 *[Insert trending song here]* 🎶"
        )
    elif query.data == 'song_new':
        await query.edit_message_text(
            "🆕 OMGGG 버디야!! A *new release*?! You wanna be the FIRST to hear it, huh?? 😳💖 "
            "I’m literally shaking giving this to you because it’s BRAND NEW, FRESH, still warm from the studio oven!! "
            "Only you get this from me first, my precious love~ 🥺💕 "
            "🎶 *[Insert new song here]* 🎶"
        )

def get_handlers():
    return [
        ('song', song_command),
        CallbackQueryHandler(song_button, pattern='^song_')
    ]
