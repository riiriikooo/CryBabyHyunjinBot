from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
import random

WAITING_FOR_BUDGET = 1

# In-memory budget data: resets on bot restart
budget_data = {}

income_reactions = [
    "Yay, 내 사랑! You got +${amount}! Our money is growing, babe~ Your balance is ${balance} now! Come here for a big hug! 💖",
    "Hey, baby! +${amount} just came in! Let’s go for that hot pot date! Balance: ${balance} 💕",
    "Money shower! +${amount} 💵 We’re the richest couple, nae 꿀! Balance: ${balance} 💞",
    "Sweetie, +${amount} added! More bubble tea coming your way~ Balance: ${balance} 🧋💖",
    "My cutie, +${amount} earned! Love and money both stacking up~ Balance: ${balance} 😘",
    "Hey, jagiya! +${amount}!! Looks like we’re getting rich! Balance: ${balance} 💸💕",
    "My 귀염둥이, you made +${amount}! Let’s hang out more! Balance: ${balance} 💖",
    "애기, +${amount} just deposited! Rich couple goals~ Balance: ${balance} 🥰"
]

expense_reactions = [
    "Oh no! -${amount} spent... My heart aches 😭 Balance: ${balance} 💔",
    "Jagi, you spent -${amount}? We can’t do that~ Balance: ${balance} 🥺",
    "Who took our bubble tea money?! -${amount}!! Balance: ${balance} I’m so mad!!",
    "My baby spent -${amount}... but I still love you, Balance: ${balance} 💖",
    "Hot pot fund lost -${amount}... I’m sad 😢 Balance: ${balance}",
    "Who stole my babe’s money?! -${amount} Balance: ${balance} I’ll protect us!!",
    "My heart cries with you… -${amount} Balance: ${balance} Love you, jagiya~",
    "Spent -${amount}... Let’s earn more, Balance: ${balance} 💪"
]

reset_reactions = [
    "Our love fund is zero! 😭 My heart is breaking...",
    "Reset to 0... but I only need you, Balance: ${balance} 💔",
    "0 now... Let’s start over, nae sarang 💖",
    "No bubble tea money... but I have you, that’s enough 🥹",
    "No money but full of love! Balance: ${balance} 💕",
    "Money gone but my love stays! Balance: ${balance}",
    "0 balance but we’re the best team, nae 꿀~",
    "Starting fresh! 0 but love is infinite! 💖"
]

def budget_start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if chat_id not in budget_data:
        budget_data[chat_id] = 0.0
    update.message.reply_text(
        f"Babe~ 🐰 Your current balance is ${budget_data[chat_id]:.2f}!\n\n"
        "Let’s start tracking money!\n"
        "➕ Type +amount to add income\n"
        "➖ Type -amount to add expense\n"
        "🔄 Type reset to reset balance\n\n"
        "What do you wanna do, jagiya~?"
    )
    return WAITING_FOR_BUDGET

def budget_action(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    text = update.message.text.strip().lower()
    balance = budget_data.get(chat_id, 0.0)

    if text.startswith("+"):
        try:
            amount = float(text[1:])
            balance += amount
            budget_data[chat_id] = balance
            reaction = random.choice(income_reactions).replace("${amount}", f"{amount:.2f}").replace("${balance}", f"{balance:.2f}")
            update.message.reply_text(reaction)
        except ValueError:
            update.message.reply_text("Oops, please write a valid number, nae sarang~ 🥺")

    elif text.startswith("-"):
        try:
            amount = float(text[1:])
            balance -= amount
            budget_data[chat_id] = balance
            reaction = random.choice(expense_reactions).replace("${amount}", f"{amount:.2f}").replace("${balance}", f"{balance:.2f}")
            update.message.reply_text(reaction)
        except ValueError:
            update.message.reply_text("Hmm? That’s not a number, baby~ 😘")

    elif text == "reset":
        budget_data[chat_id] = 0.0
        reaction = random.choice(reset_reactions).replace("${balance}", "0.00")
        update.message.reply_text(reaction)

    else:
        update.message.reply_text(
            "Baby~ try like this:\n"
            "➕ +amount : add income\n"
            "➖ -amount : add expense\n"
            "🔄 reset : reset balance\n"
            "Try again, jagiya~"
        )

    return WAITING_FOR_BUDGET

def budget_cancel(update: Update, context: CallbackContext):
    update.message.reply_text("No more money talk for now~ but I’ll always love you, nae sarang! 💖")
    return ConversationHandler.END

def get_budget_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("budget", budget_start)],
        states={
            WAITING_FOR_BUDGET: [
                MessageHandler(Filters.text & ~Filters.command, budget_action)
            ],
        },
        fallbacks=[CommandHandler("cancel", budget_cancel)],
    )
