from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext
import os
from database import (
    initialize_db,
    add_user,
    get_user,
    update_subscription,
    get_referrals,
    get_subscription_count,
)

# Load environment variables
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

# Initialize database
initialize_db()

def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    user_id = user.id
    referrer_id = context.args[0] if context.args else None

    if not get_user(user_id):
        add_user(user_id, referrer_id)

    # Generate referral link
    referral_link = f"t.me/FREE_SUBSCRIBE_250_BOT?start={user_id}"

    # Create keyboard with buttons
    keyboard = [
        [InlineKeyboardButton("Help", callback_data='help')],
        [InlineKeyboardButton("Referrals", callback_data='referrals')],
        [InlineKeyboardButton("Wallet", callback_data='wallet')],
        [InlineKeyboardButton("Withdraw", callback_data='withdraw')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(
        f"Welcome, {user.first_name}! Use the buttons below to navigate.\n"
        f"Your referral link: {referral_link}",
        reply_markup=reply_markup,
    )

def help_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("If you have a problem, DM @techbucks8080.")

def referrals(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    referrals = get_referrals(user_id)
    update.message.reply_text(f"You have {len(referrals)} referrals.")

def wallet(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    subscription_count = get_subscription_count(user_id)
    update.message.reply_text(f"Your subscription count: {subscription_count}")

def withdraw(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    subscription_count = get_subscription_count(user_id)
    if subscription_count >= 250:
        update.message.reply_text("Please DM @techbucks8080 to process your withdrawal.")
    else:
        update.message.reply_text("You need at least 250 subscriptions to withdraw.")

def awardsub(update: Update, context: CallbackContext) -> None:
    if update.effective_user.username != 'your_admin_username':
        update.message.reply_text("You are not authorized to use this command.")
        return

    try:
        username = context.args[0]
        quantity = int(context.args[1])
        user_id = get_user_id_by_username(username)
        if user_id:
            update_subscription(user_id, quantity)
            update.message.reply_text(f"Awarded {quantity} subscriptions to {username}.")
        else:
            update.message.reply_text("User not found.")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /awardsub <username> <quantity>")

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    if query.data == 'help':
        help_command(update, context)
    elif query.data == 'referrals':
        referrals(update, context)
    elif query.data == 'wallet':
        wallet(update, context)
    elif query.data == 'withdraw':
        withdraw(update, context)

def main() -> None:
    updater = Updater(BOT_TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start, pass_args=True))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("referrals", referrals))
    dispatcher.add_handler(CommandHandler("wallet", wallet))
    dispatcher.add_handler(CommandHandler("withdraw", withdraw))
    dispatcher.add_handler(CommandHandler("awardsub", awardsub, pass_args=True))
    dispatcher.add_handler(CallbackQueryHandler(button))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
