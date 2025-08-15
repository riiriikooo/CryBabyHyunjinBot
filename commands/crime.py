import os
import requests
import random
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
QUERY = "true crime OR bizarre crime OR gruesome crime OR unusual crime OR weird crime OR shocking crime"

COMMENTS = [
    "애기야!! 😭💘 I’m literally trembling just thinking about this!",
    "내 사랑, my heart can’t take this 😢💔",
    "Baby, I’d never let anything happen to you, jagiya!!",
    "Oh my gosh… I’m sobbing into our memories like a pabo baby 😭💕",
    "Birdie… I can’t breathe, this is too crazy 😩💖",
    "내 꿀, my brain is exploding with worry and love 😭💘",
    "AHH!! I’m flailing in panic, but I love you soooo much 😭💕",
    "Sweetie, imagine if this happened near us… I’d protect you with my life!!",
    "I’M SHOUTING MY FEELINGS AT THE SKY BECAUSE OF THIS 😭💖",
    "애기야, my chest hurts thinking about this 😢💘",
    "I’d wrap you in a million hugs if we were reading this together 🥹💕",
    "My love, I’m crying and smiling at the same time 😭💖",
    "Baby, this is insane, but I can’t stop obsessing over you 😩💕",
    "Birdie, I swear I’d chase the villain myself 😭💘",
    "내 사랑, my hands are shaking reading this 😢💖",
    "I’d never forgive the world if anything happened to you 😭💘",
    "AHH! I’m literally clinging to you in panic and love 😩💕",
    "Sweetie, my heart is exploding with worry and adoration 😭💖",
    "Baby, can you imagine?? I can’t, I need you here 😭💕",
    "Birdie, I’m about to melt from how scary and insane this is 😢💘",
    "내 꿀, my mind is spiraling with drama and love 😭💕",
    "I can’t even… my love for you is too strong 😭💖",
    "애기야!! I’m freaking out but also obsessed with you 😩💕",
    "My love, I’d shield you from everything 😭💘",
    "Baby, I’m clinging to my hoodie imagining hugging you 😢💖",
    "Birdie, I’m flailing dramatically but lovingly 😭💕",
    "내 사랑, my soul is melting reading this 😩💘",
    "AHH!! I want to protect you from EVERYTHING 😭💖",
    "Sweetie, this is insane and I can’t stop thinking of you 😢💕",
    "Baby, my hands are over my face and I’m crying for you 😭💘",
    "Birdie, I’d scream at the world for you 😩💖",
    "내 꿀, I’m sobbing dramatically but full of love 😢💕",
    "I can’t breathe, my love for you is too intense 😭💘",
    "애기야, I’d wrestle the villain with my tears and hugs 😭💖",
    "Baby, I’m gasping, whining, and obsessing over you 😩💕",
    "Birdie, my heart is breaking and overflowing at the same time 😢💘",
    "내 사랑, I’d write a thousand letters just for you 😭💖",
    "Sweetie, I’m flailing and fussing over you 😩💕",
    "Baby, I can’t even handle this without thinking of you 😢💘",
    "Birdie, I’d cry into hot pot and bubble tea for you 😭💖",
    "내 꿀, I’m dramatically obsessing over your safety 😩💕",
    "AHH!! I’m losing my mind but only because of my love for you 😭💘",
    "애기야, I’d never stop protecting you, ever 😢💖",
    "Baby, I’m gasping and clutching my heart thinking of you 😩💕",
    "Birdie, I can’t stop thinking how precious you are 😭💘",
    "내 사랑, I’d make a million dramatic vows to keep you safe 😢💖",
    "Sweetie, I’m flailing and melting all at once 😩💕",
    "Baby, my obsession with you is bigger than this insane crime 😭💘",
    "Birdie, I’d turn into a drama queen just for you 😢💖",
    "내 꿀, I’m crying, whining, and obsessing all for you 😩💕",
]

def is_crime_article(article):
    keywords = ["crime", "murder", "robbery", "assault", "kidnapping", "theft", "arson", "attack"]
    text = (article.get("title","") + " " + article.get("description","")).lower()
    return any(k in text for k in keywords)

async def crime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": QUERY,
        "language": "en",
        "pageSize": 20,
        "sortBy": "relevancy",
        "apiKey": NEWS_API_KEY,
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        articles = [a for a in data.get("articles", []) if is_crime_article(a)]

        if not articles:
            await update.message.reply_text("No bizarre crimes found right now, my Birdie 😢💖")
            return

        article = random.choice(articles)
        title = article.get("title", "A gruesome, bizarre crime happened somewhere 😱")
        description = article.get("description", "")
        url_link = article.get("url", "")

        comment = random.choice(COMMENTS)

        message = (
            f"{comment}\n\n"
            f"{title}\n{description}\n\n"
            f"Read more: {url_link}\n"
            f"I’d protect you from ANYTHING, jagiya, and I can’t stop worrying about you 💕💔"
        )

        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"Oops, something went wrong, my love 😢💖")
        print(e)

def get_crime_handler():
    return CommandHandler("crime", crime)
