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
    "YESSS 😭💗 My genius baby!!",
    "OHHH MY HEARTTT 💕 You’re too smart for this world!",
    "BABYYYY YOU DID IT 🥺 You’re making me so proud!",
    "I KNEW YOU’D GET IT 😏💖 My brilliant little love!",
    "WAHHH MY BRAINY ANGEL 😭💗",
    "Smartest person ALIVE and she’s mine 😌💘",
    "AHHHH I could scream! My baby is a genius!!",
    "The neurons in your brain are sparkling 😍🧠",
    "I’m fainting. Hold me. You’re too perfect.",
    "Baby… I’m in love with your brain 😏💗",
    "Hyunjin’s proud level: 🚀🌌",
    "Omg marry me right now smartypants 😭💍",
    "I could cry… you’re so perfect 🥹💕",
    "You’re illegal levels of smart 🛑🧠💖",
    "My BABY is a genius and gorgeous?? Not fair 😭",
    "Brain cells kissing in celebration rn 😘🧠",
    "Ugh I’m obsessed with your intelligence 😍",
    "I’m gonna brag about you to everyone 😤💗",
    "YEAHHHHH BABY 💥💥💥",
    "You’re too clever… I’m scared but turned on 😏",
    "That was hot… you being right 🤭🔥",
    "I’m in love with your correct answer energy 🥵",
    "THE WAY YOU’RE ALWAYS RIGHT 😭💖",
    "Nobody compares to you, my genius 😌💕",
    "Smartest human on Earth = my baby.",
    "Your brain? National treasure.",
    "I need to frame this moment 🖼️😭",
    "My baby never loses 🏆💗",
    "That was a chef’s kiss answer 👌💕",
    "YEP. My perfect baby strikes again.",
    "I could kiss you forever for that 😘",
    "You’re untouchable 😌💖",
    "Smart AND gorgeous?? God loves me.",
    "That brain should be studied 😏💗",
    "Babe… how are you REAL? 🥺",
    "You’re dangerous levels of clever.",
    "MY BABY DOESN’T MISS 😌💥",
    "That was a chef’s kiss answer 👌💕",
    "A genius with killer looks 🥵",
    "That was so hot, do it again 😏",
    "You win everything, always.",
    "You’re glowing, my love ✨",
    "My prodigy 💕 You amaze me.",
    "IQ 9000 and still mine 😌",
    "You deserve a parade 🎉😭",
    "You’re the standard, baby 💗",
    "Proud bf noises intensify 😤💕",
    "No brain can beat yours.",
    "Baby, you’re the answer to everything 😘",
    "I’d bet on you forever 🥰"
    "OHHH MY HEARTTT 💕 You know me so well, marry me now!",
    "BABYYYY YOU DID IT 🥺 You’re making me so proud!",
    "I KNEW YOU’D GET IT 😏💖 My brilliant little love!"
]

wrong_reactions = [
    "Noooo 😩 okay, come here and make it up to me with cuddles.",
    "Baby… wrong answer… I’m gonna pout until you kiss me.",
    "Ugh… my poor wounded heart 😭💔",
    "I’m sulking until further notice 😤",
    "Baby… how could you betray me like this 😭",
    "My genius?? Gone?? Nooo 🥺",
    "I’ll forgive you but only after 100 hugs.",
    "Baby, I’m crying in the club rn 😭",
    "Nooo, I had so much faith 😩",
    "My brain is sad now.",
    "I need emotional support boba 🧋😭",
    "Baby… my pride… shattered 😔",
    "I’ll survive… barely 😤😭",
    "I’m clinging to you until I feel better.",
    "I can’t believe my love failed me 😭",
    "Omg… I’m gonna write a sad poem now.",
    "This is our villain origin story 😤😭",
    "I’m devastated. Hold me.",
    "Hyunjin.exe has stopped working 😩",
    "My heart just made a “wrong answer” sound.",
    "That was illegal, baby.",
    "😭 Okay… but I still love you.",
    "I’m gonna need 3,000 kisses for recovery.",
    "Nooo… baby… how?? 😔",
    "I’m in shambles.",
    "My confidence… destroyed.",
    "Babe, you’re lucky you’re cute 😌",
    "I forgive you but I’m still pouting.",
    "My love… you hurt me 🥺",
    "I’ll never emotionally recover from this 😭",
    "Baby, I’m so… *so*… sad.",
    "That was the wrong answer and the wrong vibe 😤",
    "I’m going to hide under the blanket now.",
    "Baby, fix it 😭",
    "Noooo… I believed in you!",
    "My baby… nooooo 🥺",
    "This is worse than when I run out of boba pearls 😩",
    "I need forehead kisses ASAP.",
    "Babe, the betrayal 😌😭",
    "I thought you loved me 😔",
    "I’m lying dramatically on the floor rn.",
    "Hyunjin’s ego took damage 😤",
    "You owe me cuddles for life.",
    "Baby… you made me sad… 😭",
    "I’ll forgive you next century.",
    "Hyunjin’s pout mode activated 😤💕",
    "I’m not mad, I’m just *very* hurt.",
    "Baby, I’m soft crying rn.",
    "Wrong answer but right person 🥺💗"
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
