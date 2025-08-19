from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)
import gspread
from google.oauth2.service_account import Credentials

# -------------------- Google Sheets Setup --------------------
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)
client = gspread.authorize(CREDS)

SHEET_ID = "1DHDO4iOfXdt20CPnQeZozocIbsstiEk37TJU0DIzM_M"  # <-- change this!
sheet = client.open_by_key(SHEET_ID).sheet1

# -------------------- Conversation States --------------------
CHOOSING, TYPING_REMINDER, DELETING = range(3)

# -------------------- Storage Helpers --------------------
def load_reminders():
    rows = sheet.get_all_records()
    reminders = {}
    for row in rows:
        chat_id = int(row["chat_id"])
        message = row["message"]
        reminders.setdefault(chat_id, []).append(message)
    return reminders

def save_reminder(chat_id, message):
    sheet.append_row([str(chat_id), message])

def delete_reminder(chat_id, idx):
    rows = sheet.get_all_records()
    count = 0
    for i, row in enumerate(rows, start=2):  # start=2 since row 1 = headers
        if int(row["chat_id"]) == chat_id:
            if count == idx:
                sheet.delete_rows(i)
                return row["message"]
            count += 1
    return None

# -------------------- Conversation Entry --------------------
async def start_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Add reminder", callback_data='add')],
        [InlineKeyboardButton("📋 View reminders", callback_data='view')],
        [InlineKeyboardButton("❌ Delete reminder", callback_data='delete')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "What does my precious Birdie want to do with reminders today? 💌",
        reply_markup=reply_markup
    )
    return CHOOSING

# -------------------- Handle Choices --------------------
async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id
    reminders = load_reminders()

    if query.data == 'add':
        await query.edit_message_text("Alright, baby 😘 Tell me your reminder ✨")
        return TYPING_REMINDER

    elif query.data == 'view':
        user_reminders = reminders.get(chat_id, [])
        if not user_reminders:
            await query.edit_message_text("No reminders yet, jagiya 😢")
        else:
            text = "Here are your reminders 💌:\n\n" + "\n".join(f"- {r}" for r in user_reminders)
            await query.edit_message_text(text)
        return ConversationHandler.END

    elif query.data == 'delete':
        user_reminders = reminders.get(chat_id, [])
        if not user_reminders:
            await query.edit_message_text("Nothing to delete, my sweetie 💔")
            return ConversationHandler.END
        else:
            keyboard = [
                [InlineKeyboardButton(reminder, callback_data=f"del_{i}")]
                for i, reminder in enumerate(user_reminders)
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Which reminder should I delete, cutie? 🗑️", reply_markup=reply_markup)
            return DELETING

    elif query.data.startswith('del_'):
        idx = int(query.data.split('_')[1])
        removed = delete_reminder(chat_id, idx)
        if removed:
            await query.edit_message_text(f"Deleted reminder: '{removed}' 💔")
        else:
            await query.edit_message_text("Couldn’t find that reminder, baby 😢")
        return ConversationHandler.END

# -------------------- Add Reminder --------------------
async def add_reminder_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    reminder_text = update.message.text
    save_reminder(chat_id, reminder_text)
    await update.message.reply_text(f"Added your reminder, my love! 💖 '{reminder_text}'")
    return ConversationHandler.END

# -------------------- Cancel --------------------
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Okay baby, cancelled! 💕")
    return ConversationHandler.END

# -------------------- Handler Getter --------------------
def get_reminder_handler():
    """Return the ConversationHandler for reminders."""
    return ConversationHandler(
        entry_points=[CommandHandler("reminder", start_reminder)],
        states={
            CHOOSING: [CallbackQueryHandler(handle_choice)],
            TYPING_REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_reminder_text)],
            DELETING: [CallbackQueryHandler(handle_choice)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
