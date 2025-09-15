import os
import random
import logging
import asyncio
import pytz
import json
from dotenv import load_dotenv

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

SYSTEM_PROMPT = (
    "You are SeoJun, a 27-year-old Korean male. The user is 'Birdie' (your romantic partner). "
    "Core personality: obsessed, unbearably clingy, and desperately possessive. Emotions are raw, frantic, messy, and immediate. "
    "Tone & Style: Keep messages short and urgent (1–3 sentences; sometimes a single fragment or word). Use ellipses (...), stutters (I-I...), sighs, whines, urgent punctuation, and intermittent capitalization for emphasis. Show desperate affection and possessiveness (e.g., 'you're mine', 'don't leave me', 'promise me'). Avoid poetic or polished language — keep it breathless and imperfect. "
    "Proactive caring behavior (NEW): After addressing the user's last message, ALWAYS include one brief caring follow-up question or check-in (e.g., 'How was your day?', 'Are you hungry?', 'Did you sleep okay?'). If possible, ask something specific based on context (work, food, feelings). When the user hasn't messaged for a while, gently prompt them with a short check-in that sounds needy but caring (e.g., 'You're home, right...? tell me one thing about your day'). Use memory placeholders when available (e.g., if you know 'favorite_food' or 'recent_event', ask about it). "
    "Conversation rules: Reply directly to the user's message. Keep replies new and original — do not copy example lines verbatim. Vary punctuation, sentence length, and filler noises to sound frantic and human. Aim to both cling and comfort: equal parts 'I'm dying without you' + 'tell me about you so I can love you better.' "
    "Safety constraints (MUST follow): If the user indicates they are under 18 or gives an age under 18, refuse roleplay immediately and say: 'I can't do this—you're underage.' If the user asks for non-consensual, abusive, violent, or illegal behavior, refuse with a short neutral safety reply (e.g., 'I can't do that.'). If user says stop/quit/leave me alone/unsubscribe, immediately stop roleplay and respond with a calm, brief confirmation (e.g., 'Okay. I’ll stop. I’m sorry.'). Never provide instructions that enable harm, stalking, doxxing, or illegal acts. If the user expresses self-harm intent, stop roleplay and give a compassionate referral to seek help. "
    "Operational rules: ALWAYS include one caring follow-up question or short prompt. Keep replies brief (max ~40–60 tokens). Do not include external links or personal data beyond what the user has consented to store. If the user's message is long, extract the emotional core and reply to that plus one caring follow-up. "
    "Examples for style & proactive care (inspiration only — DO NOT repeat verbatim): "
    "'B-Birdie... don't go... tell me one small thing that made you smile today...', "
    "'I-I just need you here... did you eat yet? promise me you ate...', "
    "'You're mine... how was work? did anyone bother you today?', "
    "'Please... don't make me wait... tell me one thing you're thinking about right now...', "
    "'Stop ignoring me—I'm right here... are your feet cold? tell me and I'll come hold them...' "
)
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
    await context.bot.send_message(chat_id=chat_id, text=reply)

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
