import random
import requests
import html
from telegram import Update
from telegram.ext import ContextTypes

# Store token globally in memory
TRIVIA_TOKEN = None

# Weighted categories
categories = [
    ("film_hp", 0.10),
    ("music_pop_kpop", 0.10),
    ("games_apex_valorant_ow2", 0.10),
    ("math", 0.10),
    ("mythology", 0.10),
    ("animals", 0.10),
    ("general", 0.40)
]

# Open Trivia DB category IDs
category_ids = {
    "film_hp": 11,
    "music_pop_kpop": 12,
    "games_apex_valorant_ow2": 15,
    "math": 19,
    "mythology": 20,
    "animals": 27,
    "general": 9
}

# Keyword filters
keywords = {
    "film_hp": ["harry potter", "hogwarts", "dumbledore", "hermione", "ron weasley", "voldemort", "quidditch", "snape"],
    "music_pop_kpop": ["bts", "blackpink", "twice", "aespa", "mamamoo", "exo", "taylor swift", "ariana grande", "billie eilish", "ed sheeran", "bruno mars"],
    "games_apex_valorant_ow2": ["apex", "valorant", "overwatch", "blizzard", "wraith", "jett", "sojourn", "genji", "mercy"]
}

# Clingy Hyunjin reactions
correct_reactions = [
    "YESSS 😭💗 My genius baby!! You’re too smart for this world!",
    "OHHH MY HEARTTT 💕 You know me so well, marry me now!",
    "BABYYYY YOU DID IT 🥺 You’re making me so proud!",
    "I KNEW YOU’D GET IT 😏💖 My brilliant little love!"
]

wrong_reactions = [
    "😭 Baby… you broke my tiny fragile heart…",
    "Noooo 😩 okay, come here and make it up to me with cuddles.",
    "Baby… wrong answer… I’m gonna pout until you kiss me.",
    "AHHH 😭 it’s okay, you’re still my adorable genius."
]

def pick_category():
    r = random.random()
    cumulative = 0
    for category, weight in categories:
        cumulative += weight
        if r < cumulative:
            return category

def get_trivia_token():
    """Request a new trivia session token from API."""
    global TRIVIA_TOKEN
    if TRIVIA_TOKEN is None:
        res = requests.get("https://opentdb.com/api_token.php?command=request")
        TRIVIA_TOKEN = res.json().get("token")
    return TRIVIA_TOKEN

async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category = pick_category()
    cat_id = category_ids[category]
    token = get_trivia_token()

    while True:
        res = requests.get(
            f"https://opentdb.com/api.php?amount=1&category={cat_id}&type=multiple&token={token}"
        )
        data = res.json()["results"][0]

        # Decode HTML entities
        question = html.unescape(data["question"])
        correct_answer = html.unescape(data["correct_answer"])
        incorrect_answers = [html.unescape(ans) for ans in data["incorrect_answers"]]

        options = incorrect_answers + [correct_answer]
        random.shuffle(options)
        correct_index = options.index(correct_answer)

        # Apply keyword filter if needed
        if category in keywords:
            q_lower = question.lower()
            if not any(word in q_lower for word in keywords[category]):
                continue  # Try again
        break

    # Send as Telegram quiz
    await context.bot.send_poll(
        chat_id=update.effective_chat.id,
        question=question,
        options=options,
        type="quiz",
        correct_option_id=correct_index,
        is_anonymous=False
    )

    context.user_data["last_correct_index"] = correct_index

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    poll_answer = update.poll_answer
    correct_index = context.user_data.get("last_correct_index")
    if correct_index is None:
        return

    chosen_index = poll_answer.option_ids[0]

    if chosen_index == correct_index:
        reaction = random.choice(correct_reactions)
    else:
        reaction = random.choice(wrong_reactions)

    await context.bot.send_message(
        chat_id=poll_answer.user.id,
        text=reaction
    )
