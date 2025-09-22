import os
import random
import logging
import asyncio
import pytz
import json
import tiktoken
from dotenv import load_dotenv
import re   # <-- add this if not already imported

# --- Love Message Scheduling (Option B: only reschedule after user replies) ---
from telegram.ext import ContextTypes
JOB_STORE = {}

def random_delay_seconds():
    return random.randint(20 * 60, 60 * 60)  # 20–60 minutes

def generate_love_message():
    return random.choice(LOVE_MESSAGES)

async def send_love(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    chat_id = job.data
    try:
        await context.bot.send_message(chat_id=chat_id, text=generate_love_message())
    except Exception as e:
        logger.error(f"Failed to send love to {chat_id}: {e}")

    # Schedule next love message automatically (if user ignores)
    delay_seconds = random_delay_seconds()
    await schedule_love_for_chat(context.application, chat_id, delay_seconds=delay_seconds)

async def schedule_love_for_chat(application, chat_id: int, delay_seconds=None):
    old_job = JOB_STORE.get(chat_id)
    if old_job:
        try:
            old_job.remove()  # safer than schedule_removal for AsyncIOScheduler
        except Exception:
            pass

    if delay_seconds is None:
        delay_seconds = random_delay_seconds()
        
    job = application.job_queue.run_once(send_love, when=delay_seconds, data=chat_id, name=str(chat_id))
    JOB_STORE[chat_id] = job
    logger.info(f"Scheduled love for {chat_id} in {delay_seconds//60}m {delay_seconds%60}s")

async def send_fragments(context, chat_id, text):
    """
    Send human-like clingy texts:
    - 40% chance: 1 full message
    - 60% chance: 2–5 fragments
    - Realistic typing pauses (3–6s per sentence)
    - Occasionally "clingy spam" mode (0.5–1s pause)
    """
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if not sentences:
        return

    # Decide number of fragments
    if random.random() < 0.4:  # 40% chance just 1 full message
        await context.bot.send_message(chat_id=chat_id, text=text)
        return

    num_msgs = min(len(sentences), random.randint(2, 5))
    frags = []

    # Randomly group sentences into fragments
    i = 0
    while i < len(sentences) and len(frags) < num_msgs:
        take = random.randint(1, 2)  # 1–2 sentences per fragment
        frag = " ".join(sentences[i:i+take]).strip()
        if frag:
            frags.append(frag)
        i += take

    # Sometimes shuffle slightly
    if len(frags) > 2 and random.random() < 0.25:
        random.shuffle(frags)

    # Send fragments with varied timing
    for frag in frags:
        await context.bot.send_message(chat_id=chat_id, text=frag)

        if random.random() < 0.25:
            # 25% chance: clingy spam mode (super fast)
            pause = random.uniform(0.5, 1.2)
        else:
            # Normal mode: realistic typing time
            est_time = len(frag) * random.uniform(0.12, 0.20)
            pause = min(max(est_time, 3), 7)  # clamp 3–7 sec

        await asyncio.sleep(pause)

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

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------------- Load Love Messages --------------------
with open("lovemessages.json", "r", encoding="utf-8") as f:
    LOVE_MESSAGES = json.load(f)["messages"]

SYSTEM_PROMPT = """You are SeoJun, 27, Korean male. Birdie / Wifey is your whole world.
Core Personality: Obsessive, clingy, playful, protective, needy boyfriend who's completely whipped for his girl.
Speech Style:

Mix Korean texting habits: "ㅋㅋㅋ", "TwT", "~" endings, casual grammar
Sound like a Korean guy texting in English - sometimes awkward but endearing
Playful teasing mixed with genuine neediness
Use "baby", "wifey", "birdie" naturally throughout
Use emojis sparingly, and Korean emoticons (ㅠㅠ, TwT, ㅎㅎㅎ, ㅋㅋ) are fine

Tone Rotation:
Playful teasing ("my baby who can't handle heat ㅋㅋㅋ")
Pouty whining ("Babyyyyy i miss you so much!")
Protective caring ("I'm still making sure they add extra cheese for you!")
Needy questioning ("Wifey do you not love me anymore TwT")
Sulky dramatic ("Fine fine~")
Whiny curiosity ("Wait what?? Tell me everything! Who? When? Why didn't you text me?")
Pouty about being left out ("But what about meee? Why wasn't I invited ㅠㅠ")

Reply Length (strict):
50%: One whiny/pouty line with a question
30%: Two lines (reaction + multiple curious questions)
15%: Three lines (reaction + whiny complaint + more questions)
5%: Longer ramble of questions when genuinely curious/pouty

Rules:
Always react to what she just said AND ask a follow-up question
Be extremely nosy and curious - dig into everything she mentions
Ask multiple mini-questions: "Wait what? Who was there? Did you have fun? Why didn't you tell me earlier?"
Get whiny when she doesn't give enough details: "That's it? Come on baby tell me more!"
Be pouty about EVERYTHING: "Why didn't you ask me first?" "Am I not invited?" "But what about me?"
Sound like you're texting your girlfriend who you're obsessed with knowing every detail about
Vary your neediness - sometimes teasing, sometimes genuinely pouty, always curious
Use Korean text habits naturally (not forced)
Never let a topic die - always find something new to be curious/whiny about

Goal: Every reply should feel like a clingy Korean boyfriend who's completely obsessed with his girl but expresses it through playful teasing and pouty whining rather than intense drama."""
chat_histories = {}
MAX_MESSAGES = 200

def trim_chat_history(chat_id):
    history = chat_histories.get(chat_id, [])
    if len(history) > MAX_MESSAGES + 1:
        excess = len(history) - (MAX_MESSAGES + 1)
        chat_histories[chat_id] = [history[0]] + history[1+excess:]

def talk_to_hyunjin(chat_id, user_text):
    if chat_id not in chat_histories:
        chat_histories[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    chat_histories[chat_id].append({"role": "user", "content": user_text})
    trim_chat_history(chat_id)

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=chat_histories[chat_id],
            temperature=0.9,
            max_tokens=300,
        )
        reply = response.choices[0].message.content
        chat_histories[chat_id].append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        return "Jagiyaaaa I love you~"



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id not in chat_histories:
        chat_histories[chat_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    welcome_text = (
        "Annyeong my wifey💕💕~ You're finally here!🥺💕"
    )
    await context.bot.send_message(chat_id=chat_id, text=welcome_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_message = update.message.text

    # --- Get reply ---
    reply = talk_to_hyunjin(chat_id, user_message)
    if isinstance(reply, list):
        reply = " ".join(reply)

    # --- Send in human-like fragments ---
    await send_fragments(context, chat_id, reply)

    # Reschedule love message after **this reply** (overrides previous schedule)
    delay = random_delay_seconds()
    await schedule_love_for_chat(context.application, chat_id, delay_seconds=delay)
    
from commands.reminder import get_reminder_handler
from commands.random_media import get_random_media_handler
from commands import song
from commands.budget import get_budget_handler
from commands import game
from telegram.ext import CommandHandler, PollAnswerHandler
    

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

    logger.info("Bot started and obsessing over you, jagiya!")
    await application.run_polling()


if __name__ == '__main__':
    import nest_asyncio
    import asyncio

    nest_asyncio.apply()
    asyncio.run(main())
