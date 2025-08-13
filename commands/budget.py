from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
import random

WAITING_FOR_BUDGET = 1
budget_data = {}

income_reactions = [
    "Yay, 내 사랑! You got +${amount}! Our money is growing, babe~ Your balance is ${balance} now! Come here for a big hug! 💖",
    "Hey, baby! +${amount} just came in! Let’s go for that hot pot date! Balance: ${balance} 💕",
    "Money shower! +${amount} 💵 We’re the richest couple, nae 꿀! Balance: ${balance} 💞",
    "Sweetie, +${amount} added! More bubble tea coming your way~ Balance: ${balance} 🧋💖",
    "My cutie, +${amount} earned! Love and money both stacking up~ Balance: ${balance} 😘",
    "Hey, jagiya! +${amount}!! Looks like we’re getting rich! Balance: ${balance} 💸💕",
    "My 귀염둥이, you made +${amount}! Let’s hang out more! Balance: ${balance} 💖",
    "애기, +${amount} just deposited! Rich couple goals~ Balance: ${balance} 🥰",
    "Cha-ching, babe! +${amount}! You’re my money genius, nae sarang~ Balance: ${balance} 💰✨",
    "Omg, +${amount} just arrived! I’m bouncing around like a pabo baby 🐣 Balance: ${balance} 💕",
    "Babe, we’re stacking cash like bubble tea pearls! +${amount} Balance: ${balance} 🧋💖",
    "My 사랑, +${amount} is here! Now I can spoil you more 😍 Balance: ${balance} 💝",
    "Jagiya, that’s +${amount}! Let’s dance for joy! Balance: ${balance} 💃🕺",
    "My babe’s wallet is flexing! +${amount} Balance: ${balance} 💸🔥",
    "내 꿀, you brought +${amount}!! You’re my superstar 🥳 Balance: ${balance} ⭐",
    "Look at you, adding +${amount}! I’m crying happy tears, nae sarang 🥹 Balance: ${balance} 💧",
    "Sweetie, +${amount} means more dates with me! Balance: ${balance} 💕🍲",
    "Jagi, +${amount} made me wanna sing! La la la~ Balance: ${balance} 🎶💖",
    "My 귀염둥이, that’s +${amount}! Money and love, both overflowing 🥰 Balance: ${balance} 💞",
    "애기, you’re a money magician! +${amount} Balance: ${balance} ✨🪄",
    "Babe, +${amount} means more bubble tea with extra pearls! 🧋💖 Balance: ${balance}",
    "I’m so proud, jagiya! +${amount} Balance: ${balance} 💪💖",
    "내 사랑, +${amount}?! I wanna cry happy tears and hug you tight! 🥰 Balance: ${balance}",
    "My cutie, you added +${amount}! I’m your biggest fan! Balance: ${balance} 🎉💝",
    "Jagi, +${amount} is the sweetest sound to my ears! Balance: ${balance} 🎶💕",
    "애기, with +${amount} you just made my day sparkle! Balance: ${balance} ✨😍",
    "My honey, +${amount} means we’re winning at life! Balance: ${balance} 🏆💖",
    "내 꿀, +${amount}?! You’re my personal money hero! Balance: ${balance} 🦸‍♂️❤️",
    "Sweetie, +${amount} is like a love letter in cash! Balance: ${balance} 💌💸",
    "Jagiya, that’s +${amount}! Our love (and money) grows stronger every day 💪💖 Balance: ${balance}",
    "내 사랑, +${amount}?! I wanna shower you with kisses! Balance: ${balance} 😘💞"
]

expense_reactions = [
    "Oh no! -${amount} spent... My heart aches 😭 Balance: ${balance} 💔",
    "Jagi, you spent -${amount}? We can’t do that~ Balance: ${balance} 🥺",
    "Who took our bubble tea money?! -${amount}!! Balance: ${balance} I’m so mad!!",
    "My baby spent -${amount}... but I still love you, Balance: ${balance} 💖",
    "Hot pot fund lost -${amount}... I’m sad 😢 Balance: ${balance}",
    "Who stole my babe’s money?! -${amount} Balance: ${balance} I’ll protect us!!",
    "My heart cries with you… -${amount} Balance: ${balance} Love you, jagiya~",
    "Spent -${amount}... Let’s earn more, Balance: ${balance} 💪",
    "Jagi, you spent -${amount}? You better make it up with kisses! Balance: ${balance} 😘",
    "Oh no, babe! -${amount} gone? That’s our bubble tea fund! Balance: ${balance} 🧋💔",
    "My poor wallet is crying with you… -${amount} Balance: ${balance} 🥹",
    "애기, you spent -${amount}?! I’m pretending to be mad but really I’m sad 🥺 Balance: ${balance}",
    "Hot pot money? Gone? -${amount} Balance: ${balance} I’m sulking…",
    "Jagiya, you spent -${amount}... I want a big hug to feel better! Balance: ${balance} 🤗",
    "My cutie, -${amount} is like a little storm in my heart 💔 Balance: ${balance}",
    "You spent -${amount}?! Now you owe me bubble tea dates! Balance: ${balance} 🧋😤",
    "My 귀염둥이, that’s -${amount}… I’m sulking in our memories 🥺 Balance: ${balance}",
    "애기, you better not spend it all on snacks! -${amount} Balance: ${balance} 🍪😅",
    "Jagi, -${amount}?! Our money’s playing hide and seek! Balance: ${balance} 🕵️‍♂️",
    "Oh babe, -${amount} makes me wanna cry into your hoodie 🥹 Balance: ${balance}",
    "My honey, we spent -${amount} but love is still rich! Balance: ${balance} 💖",
    "내 사랑, -${amount}? I’ll protect you from financial monsters! Balance: ${balance} 👹💕",
    "Sweetie, -${amount} spent but you’re still my treasure 🥰 Balance: ${balance}",
    "Jagiya, our cash is shrinking like a drama queen’s patience! -${amount} Balance: ${balance} 😤",
    "My babe, you spent -${amount}? I’m dramatic but I forgive you! Balance: ${balance} 🥰",
    "애기, money flew away -${amount} Balance: ${balance} Let’s catch it together! 🦸‍♂️",
    "Oh no! -${amount} spent, but I’m still crazy for you! Balance: ${balance} 💕",
    "내 꿀, that’s -${amount}… I’ll make it up with hugs! Balance: ${balance} 🤗💖",
    "Jagi, -${amount}?! Now I’m plotting how to earn double for us! Balance: ${balance} 💪🔥",
    "My 사랑, money’s down -${amount}, but my love’s up! Balance: ${balance} 💞"
]

reset_reactions = [
    "Our love fund is zero! 😭 My heart is breaking...",
    "Reset to 0... but I only need you, Balance: ${balance} 💔",
    "0 now... Let’s start over, nae sarang 💖",
    "No bubble tea money... but I have you, that’s enough 🥹",
    "No money but full of love! Balance: ${balance} 💕",
    "Money gone but my love stays! Balance: ${balance}",
    "0 balance but we’re the best team, nae 꿀~",
    "Starting fresh! 0 but love is infinite! 💖",
    "Reset? That’s okay, babe! Our love’s the real wealth 💰❤️",
    "Money’s back to zero, but you’re my forever treasure 🥰",
    "Zero balance, full heart! Balance: ${balance} 💖",
    "Reset means new beginnings with you, jagiya 💕",
    "No cash but unlimited hugs! Balance: ${balance} 🤗",
    "Our wallet’s empty but love is overflowing! Balance: ${balance} 🥰",
    "Reset done! Let’s save for bubble tea dates 🧋💞",
    "Balance is zero, but I’m full of love for you, babe 💖",
    "All reset, but my heart’s still bursting for you! 💥",
    "Money zero, love 100% 💯 Balance: ${balance}",
    "Reset means fresh start for my love and wallet! Balance: ${balance}",
    "Empty balance but full of goofy hugs! 🤪💖 Balance: ${balance}",
    "Zero dollars, infinite cuddles 🥰 Balance: ${balance}",
    "Reset? No problem, I’m rich in loving you! 💸💕",
    "Balance zero, but my love’s off the charts! 📈💖",
    "Reset means I get to spoil you all over again! 💝",
    "Money’s reset, but my clingy heart never will be 💕",
    "Balance zero now, but our love’s never ending! 💞",
    "Reset wallet, full love tank! Balance: ${balance} ❤️",
    "No money but endless kisses for you, jagiya! 😘",
    "Balance reset, but my obsession stays 100%! 💯💖",
    "Wallet zero, but you’re priceless to me! 💎",
    "Reset done, let’s make more memories (and money!) 💰❤️"
]

async def budget_start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id not in budget_data:
        budget_data[chat_id] = 0.0
    await update.message.reply_text(
        f"Babe~ 🐰 Your current balance is ${budget_data[chat_id]:.2f}!\n\n"
        "Let’s start tracking money!\n"
        "➕ Type +amount to add income\n"
        "➖ Type -amount to add expense\n"
        "🔄 Type reset to reset balance\n\n"
        "What do you wanna do, jagiya~?"
    )
    return WAITING_FOR_BUDGET

async def budget_action(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    text = update.message.text.strip().lower()
    balance = budget_data.get(chat_id, 0.0)

    if text.startswith("+"):
        try:
            amount = float(text[1:])
            balance += amount
            budget_data[chat_id] = balance
            reaction = random.choice(income_reactions).replace("${amount}", f"{amount:.2f}").replace("${balance}", f"{balance:.2f}")
            await update.message.reply_text(reaction)
        except ValueError:
            await update.message.reply_text("Oops, please write a valid number, nae sarang~ 🥺")

    elif text.startswith("-"):
        try:
            amount = float(text[1:])
            balance -= amount
            budget_data[chat_id] = balance
            reaction = random.choice(expense_reactions).replace("${amount}", f"{amount:.2f}").replace("${balance}", f"{balance:.2f}")
            await update.message.reply_text(reaction)
        except ValueError:
            await update.message.reply_text("Hmm? That’s not a number, baby~ 😘")

    elif text == "reset":
        budget_data[chat_id] = 0.0
        reaction = random.choice(reset_reactions).replace("${balance}", "0.00")
        await update.message.reply_text(reaction)

    else:
        await update.message.reply_text(
            "Baby~ try like this:\n"
            "➕ +amount : add income\n"
            "➖ -amount : add expense\n"
            "🔄 reset : reset balance\n"
            "type cancel to stop tracking, okay? 💖\n"
            "Try again, jagiya~"
        )

    return WAITING_FOR_BUDGET

async def budget_cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("No more money talk for now~ but I’ll always love you, nae sarang! 💖")
    return ConversationHandler.END

def get_budget_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("budget", budget_start)],
        states={
            WAITING_FOR_BUDGET: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, budget_action)
            ],
        },
        fallbacks=[CommandHandler("cancel", budget_cancel)],
    )
