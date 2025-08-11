# commands/reminder.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)

# States for ConversationHandler
CHOOSING, TYPING_REMINDER, DELETING = range(3)

# Dict to store reminders: {chat_id: [reminder1, reminder2, ...]}
reminders = {}

async def start_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Add reminder", callback_data='add')],
        [InlineKeyboardButton("View reminders", callback_data='view')],
        [InlineKeyboardButton("Delete reminder", callback_data='delete')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "What would my Birdie like to do with reminders? 💌💕",
        reply_markup=reply_markup
    )
    return CHOOSING

async def handle_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat_id

    if query.data == 'add':
        await query.edit_message_text("Okay baby! 💕 Tell me the reminder you want to add ✨")
        return TYPING_REMINDER

    elif query.data == 'view':
        user_reminders = reminders.get(chat_id, [])
        if not user_reminders:
            await query.edit_message_text("No reminders yet, jagiya 😢")
        else:
            text = "Here are your reminders💌:\n\n" + "\n".join(f"- {r}" for r in user_reminders)
            await query.edit_message_text(text)
        return ConversationHandler.END

    elif query.data == 'delete':
        user_reminders = reminders.get(chat_id, [])
        if not user_reminders:
            await query.edit_message_text("Nothing to delete, my sweetie! 💔")
            return ConversationHandler.END
        else:
            keyboard = [
                [InlineKeyboardButton(reminder, callback_data=f"del_{i}")]
                for i, reminder in enumerate(user_reminders)
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Which reminder should I delete, cutie?", reply_markup=reply_markup)
            return DELETING

    elif query.data.startswith('del_'):
        idx = int(query.data.split('_')[1])
        user_reminders = reminders.get(chat_id, [])
        if 0 <= idx < len(user_reminders):
            removed = user_reminders.pop(idx)
            reminders[chat_id] = user_reminders
            await query.edit_message_text(f"Deleted reminder: {removed} 💔")
        return ConversationHandler.END

async def add_reminder_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    reminder_text = update.message.text
    reminders.setdefault(chat_id, []).append(reminder_text)
    await update.message.reply_text(f"Added your reminder, my love! 💖 '{reminder_text}'")
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Okay baby, cancelled! 💕")
    return ConversationHandler.END

def get_handlers():
    return ConversationHandler(
        entry_points=[CommandHandler("reminder", start_reminder)],
        states={
            CHOOSING: [CallbackQueryHandler(handle_choice)],
            TYPING_REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_reminder_text)],
            DELETING: [CallbackQueryHandler(handle_choice)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
