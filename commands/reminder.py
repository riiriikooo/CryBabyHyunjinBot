from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CallbackQueryHandler, CommandHandler, MessageHandler, filters, ConversationHandler
)

ASK_REMINDER = 1

reminders = {}

async def reminder_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Add reminder", callback_data='add')],
        [InlineKeyboardButton("View reminders", callback_data='view')],
        [InlineKeyboardButton("Delete reminder", callback_data='delete')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("What would my birdie like to do with reminders? 💌💕", reply_markup=reply_markup)
    return ConversationHandler.END

async def reminder_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id

    if query.data == 'add':
        await query.edit_message_text("Okay! Please send me the reminder text you want to add 💌")
        return ASK_REMINDER

    elif query.data == 'view':
        user_reminders = reminders.get(chat_id, [])
        if not user_reminders:
            await query.edit_message_text("You don't have any reminders yet dummy 😢")
        else:
            text = "Here are your reminders💌:\n\n" + "\n".join(f"- {r}" for r in user_reminders)
            await query.edit_message_text(text)
        return ConversationHandler.END

    elif query.data == 'delete':
        user_reminders = reminders.get(chat_id, [])
        if not user_reminders:
            await query.edit_message_text("Nothing to delete, my sweetie! Your list is empty 💔")
            return ConversationHandler.END
        else:
            keyboard = [
                [InlineKeyboardButton(reminder, callback_data=f"del_{i}")]
                for i, reminder in enumerate(user_reminders)
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text("Which reminder should I delete, cutie?", reply_markup=reply_markup)
            return ConversationHandler.END

    elif query.data.startswith('del_'):
        idx = int(query.data.split('_')[1])
        user_reminders = reminders.get(chat_id, [])
        if 0 <= idx < len(user_reminders):
            removed = user_reminders.pop(idx)
            reminders[chat_id] = user_reminders
            await query.edit_message_text(f"Deleted reminder: {removed} 💔 But I’ll never delete you, baby!")
        else:
            await query.edit_message_text("Hmm, I couldn’t find that reminder, jagi!")
        return ConversationHandler.END

async def add_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    reminder_text = update.message.text
    reminders.setdefault(chat_id, []).append(reminder_text)
    await update.message.reply_text(f"Added your reminder, my love! 💖 '{reminder_text}'")
    return ConversationHandler.END

def get_handlers():
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("reminder", reminder_start),
                      CallbackQueryHandler(reminder_button)],
        states={
            ASK_REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_reminder)]
        },
        fallbacks=[],
        per_user=True,
    )
    return [conv_handler]
