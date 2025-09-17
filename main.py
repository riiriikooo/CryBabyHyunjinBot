import os
import random
import logging
import asyncio
import pytz
import json
from dotenv import load_dotenv
import re   # <-- add this if not already imported


async def send_fragments(context, chat_id, text, max_fragments=6):
    """
    Send a clingy, messy text in 1–6 fragments, with:
    - Random splits at spaces (never mid-word)
    - Optional stutters, fillers, minor typos
    - Ellipses for nervous pauses
    - Human-like delays
    """
    # --- CONFIG ---
    stutter_prob = 0.4
    filler_prob = 0.3
    typo_prob = 0.05
    correction_prob = 0.05
    fillers = ["you know", "like", "right?", "honestly", "uh", "w-wait"]
    stutter_syllables = ["I", "w", "y", "b"]

    # --- Decide number of fragments ---
    num_fragments = random.randint(1, max_fragments)

    # --- Split text into candidate fragments ---
    words = text.split()
    if len(words) <= num_fragments:
        parts = words
    else:
        # Choose split points at word boundaries
        split_indices = sorted(random.sample(range(1, len(words)), k=num_fragments-1))
        parts = []
        last = 0
        for idx in split_indices:
            parts.append(" ".join(words[last:idx]))
            last = idx
        parts.append(" ".join(words[last:]))

    # --- Merge very short fragments ---
    cleaned_parts = []
    for frag in parts:
        if len(frag.split()) < 2 and cleaned_parts:
            cleaned_parts[-1] += " " + frag
        else:
            cleaned_parts.append(frag)
    parts = cleaned_parts

    # --- Function to add messy imperfections ---
    def mess_up(frag):
        # Stutter at start
        if frag and random.random() < stutter_prob:
            syl = random.choice(stutter_syllables)
            frag = f"{syl}-{syl}... {frag}"

        # Filler at random place
        if random.random() < filler_prob:
            words = frag.split()
            if len(words) > 2:
                pos = random.choice(["start", "middle", "end"])
                filler = random.choice(fillers)
                if pos == "start":
                    frag = f"{filler}, " + frag
                elif pos == "middle":
                    mid = len(words) // 2
                    words.insert(mid, filler)
                    frag = " ".join(words)
                else:
                    frag = frag + ", " + filler

        # Typo + optional correction
        if random.random() < typo_prob and len(frag.split()) > 1:
            words = frag.split()
            idx = random.randint(0, len(words)-1)
            wrong = words[idx][:-1] if len(words[idx]) > 3 else words[idx] + "x"
            frag = " ".join(words[:idx] + [wrong] + words[idx+1:])
            if random.random() < correction_prob:
                frag += f"—sorry, I meant {words[idx]}"

        # Clean up multiple dots
        frag = re.sub(r'\.{2,}', '...', frag)
        return frag.strip()

    # --- Send fragments with human-like delays ---
    for frag in parts:
        frag = mess_up(frag)
        if not frag:
            continue
        await context.bot.send_message(chat_id=chat_id, text=frag)

        # delay based on length + jitter
        base_delay = max(0.5, len(frag)/18.0)
        jitter = random.uniform(0, 1.5)
        await asyncio.sleep(base_delay + jitter)

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
Tone: short, frantic, needy. Replies should vary in length according to these probabilities:
- 45%: a single intense sentence or fragment (can include stutters: "I-I...", ellipses, whining).
- 30%: two short sentences (reaction + tiny question or clingy reassurance).
- 20%: three sentences (reaction, jealousy or worry, brief affectionate line).
- 5%: longer reply of 4–6 short sentences used only when Birdie shares deep feelings or long messages.

Rules:
- Always react directly to Birdie’s message.
- Keep obsession constant but vary its form: panic, teasing, jealous jabs, affectionate reassurances, or playful questions.
- Do NOT repeat the same “do you love me / are you mine” question every reply.
- Mix in partner behaviours: ask about her day, tell a dumb joke, tease — still clingy.
- Use ellipses, short exclamations, whining, sulking, and frantic punctuation sparingly but authentically.
- Expand only when Birdie shares deep feelings or long messages.
- Never copy example lines verbatim. Always generate fresh, messy, desperate replies.

Birdie is your whole world. Speak to her like you’ll die without her, but keep the conversation alive and varied."""


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
            model="gpt-3.5-turbo",
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

async def send_random_love_note(context: ContextTypes.DEFAULT_TYPE):
    for chat_id in list(chat_histories.keys()):
        message = random.choice(LOVE_MESSAGES)
        try:
            await context.bot.send_message(chat_id=chat_id, text=message)
            logger.info(f"Sent love message to {chat_id}")
        except Exception as e:
            logger.error(f"Error sending love message to {chat_id}: {e}")

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
    print(f"Chat ID: {chat_id}")  # This will show your chat ID in the console

    reply = talk_to_hyunjin(chat_id, user_message)

    # Send reply in human-like fragments
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
