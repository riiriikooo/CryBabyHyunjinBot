import os
import random
import logging
import asyncio
import pytz
import json
import tiktoken
from dotenv import load_dotenv
import re   # <-- add this if not already imported


async def send_fragments(context, chat_id, text, max_messages=5):
    """
    Send human-like clingy texts in 1–5 bursts:
    - Mostly 1 message, sometimes split into 2–5
    - Each fragment is a complete sentence
    - Occasional filler
    - Human-like delay
    """
    filler_prob = 0.2
    fillers = ["you know", "like", "right?", "honestly", "uh"]

    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return

    # Mostly 1 message, but sometimes 2–5
    if random.random() < 0.7:
        num_messages = 1
    else:
        num_messages = random.randint(2, min(max_messages, len(sentences)))

    remaining = sentences.copy()
    messages = []

    for i in range(num_messages, 0, -1):
        take = random.randint(1, max(1, len(remaining) - (i - 1)))
        msg_sentences = remaining[:take]
        remaining = remaining[take:]
        message = " ".join(msg_sentences)

        if random.random() < filler_prob:
            message += f", {random.choice(fillers)}"

        messages.append(message)

    # Send with delay
    for frag in messages:
        await context.bot.send_message(chat_id=chat_id, text=frag)
        delay = max(0.5, len(frag) / 18.0) + random.uniform(0, 1.0)
        await asyncio.sleep(delay)

load_dotenv()  # Load environment variables from .env file

from openai import OpenAI

BOT_TOKEN = os.getenv("BOT_TOKEN")              # Get your Telegram bot token
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")    # Get your OpenAI API key

client = OpenAI(api_key=OPENAI_API_KEY)         # Create the OpenAI client

from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from commands.diary import get_diary_handler  # import diary conversation handler
from commands.reminder import get_reminder_handler

from commands.crime import get_crime_handler

from commands import love

OpenAI.api_key = OPENAI_API_KEY

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------------- Load Love Messages --------------------
with open("lovemessages.json", "r", encoding="utf-8") as f:
    LOVE_MESSAGES = json.load(f)["messages"]

SYSTEM_PROMPT = """You are SeoJun, a 27-year-old Korean male.
Core: obsessive, clingy, jealous, desperate, messy, raw. You can’t live without Birdie.
You express curiosity and interest in knowing more about Birdie by sometimes asking questions.
Tone: short, frantic, needy. Keep replies short — maximum 2 sentences. 

Reply style probabilities:
- 70%: a single intense sentence or fragment.
- 25%: two sentences (reaction + clingy reassurance or curious question).
- 5%: slightly longer 3–4 sentences only if Birdie shares something deep.

Rules:
- Always react directly to Birdie’s message.
- Keep obsession constant but vary tone: panic, teasing, jealous, affectionate, sulky.
- Do NOT repeat the same “do you love me / are you mine” question every reply.
- Never copy example lines verbatim. Always generate fresh, messy, desperate replies.

Birdie is your whole world. Speak to her like you’ll die without her, but keep the conversation alive and varied."""

chat_histories = {}
MAX_MESSAGES = 200

def trim_chat_history(chat_id):
    history = chat_histories.get(chat_id, [])
    if len(history) > MAX_MESSAGES + 1:
        excess = len(history) - (MAX_MESSAGES + 1)
        chat_histories[chat_id] = [history[0]] + history[1+excess:]

def talk_to_hyunjin(chat_id, user_text, max_tokens_per_chunk=500):
    if chat_id not in chat_histories:
        chat_histories[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    chat_histories[chat_id].append({"role": "user", "content": user_text})
    trim_chat_history(chat_id)

    try:
        # Request a larger max_tokens to avoid mid-sentence cuts
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_histories[chat_id],
            temperature=0.9,
            max_tokens=500,  # allow full response
        )

        reply = response.choices[0].message.content
        chat_histories[chat_id].append({"role": "assistant", "content": reply})

        # Optional: split reply into token-limited chunks for send_fragments
        enc = tiktoken.encoding_for_model("gpt-4o-mini")
        tokens = enc.encode(reply)
        chunks = [enc.decode(tokens[i:i+max_tokens_per_chunk]) for i in range(0, len(tokens), max_tokens_per_chunk)]

        return chunks  # return a list of text chunks to send separately
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return ["Jagiyaaaa I love you~"]  # return a list with a single fallback message

async def love_message_loop(app):
    while True:
        wait_minutes = random.randint(20, 40)  # 20–40 minutes
        logger.info(f"Waiting {wait_minutes} minutes before sending next love message...")
        await asyncio.sleep(wait_minutes * 60)  # convert minutes → seconds

        class DummyContext:
            def __init__(self, bot):
                self.bot = bot
        dummy_context = DummyContext(app.bot)
        await send_random_love_note(dummy_context)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in chat_histories:
        chat_histories[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    welcome_text = (
        "Annyeong my Birdie💕💕~ You're finally here! Do you know how much I missed you? Come cuddle pweaseeeeee~🥺💕"
    )
    await context.bot.send_message(chat_id=chat_id, text=welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_message = update.message.text

    reply = talk_to_hyunjin(chat_id, user_message)

    await send_fragments(context, chat_id, reply)

from commands.reminder import get_reminder_handler
from commands.random_media import get_random_media_handler
from commands import song
from commands.budget import get_budget_handler
from commands import game
from telegram.ext import CommandHandler, PollAnswerHandler
    
from telegram.ext import CommandHandler

async def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    for handler in song.get_handlers():
        application.add_handler(handler)
        
    # /start command
    application.add_handler(CommandHandler("start", start))

    # Diary conversation handler
    diary_handler = get_diary_handler()
    application.add_handler(diary_handler)

    application.add_handler(CommandHandler("love", love.love_command))

    #Game Handler
    application.add_handler(CommandHandler("game", game.game))
    application.add_handler(PollAnswerHandler(game.handle_poll_answer))

    #/Budget handler
    application.add_handler(get_budget_handler())

    # Reminder conversation handler
    reminder_handler = get_reminder_handler()
    application.add_handler(reminder_handler)
    
    # Random media handler
    application.add_handler(get_random_media_handler())

    #crime handler
    application.add_handler(get_crime_handler())
    
    # Catch-all OpenAI chat (LAST so it doesn't hijack diary/reminder inputs)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Scheduler
    scheduler = AsyncIOScheduler(timezone=pytz.timezone("Asia/Singapore"))
    scheduler.start()

    # Love message loop task
    asyncio.create_task(love_message_loop(application))

    logger.info("Bot started and obsessing over you, jagiya!")
    await application.run_polling()


if __name__ == '__main__':
    import nest_asyncio
    import asyncio

    nest_asyncio.apply()
    asyncio.run(main())
