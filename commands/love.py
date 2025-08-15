import random
from telegram import Update
from telegram.ext import ContextTypes
import os

# Path to your love.txt file
LOVE_FILE_PATH = os.path.join(os.path.dirname(__file__), "love.txt")

# Load all love messages from love.txt
try:
    with open(LOVE_FILE_PATH, "r", encoding="utf-8") as f:
        love_messages = [line.strip() for line in f if line.strip()]
except FileNotFoundError:
    love_messages = ["Oh no, Ririko! I can’t find my love messages! 🥺💖"]

# The command handler function for /love
async def love_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Sends a random chaotic, clingy, obsessive, goofy Hyunjin love message
    from love.txt.
    """
    if not love_messages:
        # fallback if file is empty
        await update.message.reply_text("My love exploded into chaos! No messages found 😭💖")
        return

    # Choose a random message
    message = random.choice(love_messages)

    # Send the message
    await update.message.reply_text(message)
