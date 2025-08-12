import requests
import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, CallbackQueryHandler

API_KEY = "ed4e400ccceadafb3727598017e5ccf5"
BASE_URL = "http://ws.audioscrobbler.com/2.0/"

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

def fetch_lastfm_tracks(method, params):
    """Helper to fetch data from Last.fm"""
    params.update({
        'api_key': API_KEY,
        'format': 'json'
    })
    try:
        r = requests.get(BASE_URL, params=params, timeout=5)
        r.raise_for_status()
        data = r.json()
        return data
    except Exception as e:
        return None

async def song_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'song_trending':
        # Get top tracks globally
        data = fetch_lastfm_tracks('chart.gettoptracks', {'method': 'chart.gettoptracks', 'limit': 20})
        if data and 'tracks' in data:
            track = random.choice(data['tracks']['track'])
            song = f"{track['name']} — {track['artist']['name']}"
        else:
            song = "Couldn’t fetch trending songs right now 🥺"
        await query.edit_message_text(
            f"🌟 AAAAH 버디야aa!! TRENDING?! You want the *it* song so you’re the prettiest, coolest, most perfect human alive?? 😭💞\n"
            f"Here’s what I found for you, 내 사랑:\n🎶 {song} 🎶"
        )

    elif query.data == 'song_hidden':
        # Get a mix of not-top tracks by searching for tags
        tags = ['indie', 'underground', 'lofi', 'jazz', 'folk', 'bedroom pop']
        tag = random.choice(tags)
        data = fetch_lastfm_tracks('tag.gettoptracks', {'method': 'tag.gettoptracks', 'tag': tag, 'limit': 50})
        if data and 'tracks' in data:
            track = random.choice(data['tracks']['track'])
            song = f"{track['name']} — {track['artist']['name']} ({tag} gem)"
        else:
            song = "Couldn’t find a hidden gem right now 🥺"
        await query.edit_message_text(
            f"💎 OH MY GOSH 버디야!! You picked *Hidden Gem*! 😭💖\n"
            f"Rare, sparkly, and gorgeous—just like you~\n🎶 {song} 🎶"
        )

    elif query.data == 'song_new':
        # Last.fm doesn’t have a direct "new release" so we fake it by getting top tracks from the last week
        data = fetch_lastfm_tracks('chart.gettoptracks', {'method': 'chart.gettoptracks', 'limit': 50})
        if data and 'tracks' in data:
            track = random.choice(data['tracks']['track'])
            song = f"{track['name']} — {track['artist']['name']}"
        else:
            song = "Couldn’t fetch new releases right now 🥺"
        await query.edit_message_text(
            f"🆕 OMGGG 버디야!! You want the *freshest* track?? 😳💖\n"
            f"Hot from the studio oven just for you, 내 꿀~\n🎶 {song} 🎶"
        )

def get_handlers():
    return [
        ('song', song_command),
        CallbackQueryHandler(song_button, pattern='^song_')
    ]
