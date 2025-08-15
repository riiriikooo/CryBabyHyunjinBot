import random
from telegram import Update
from telegram.ext import ContextTypes

# The /love command
async def love(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Read all love messages from love.txt
    try:
        with open("love.txt", "r", encoding="utf-8") as f:
            # Split messages by the separator
            love_messages = f.read().split("===\n")
    except FileNotFoundError:
        love_messages = ["Oops… no love messages found 😢💖"]

    # Pick a random message
    message = random.choice(love_messages).strip()

    # Send it
    await context.bot.send_message(chat_id=chat_id, text=message)

# Optional: a function to register this command in your main.py
def register(app):
    from telegram.ext import CommandHandler
    app.add_handler(CommandHandler("love", love))
