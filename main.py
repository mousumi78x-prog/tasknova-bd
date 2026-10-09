import os
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

db = sqlite3.connect("tasknova.db", check_same_thread=False)
db.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance REAL DEFAULT 0
)
""")
db.commit()

keyboard = ReplyKeyboardMarkup(
    [
        ["📋 Tasks", "💰 Balance"],
        ["👥 Refer", "💳 Withdraw"],
    ],
    resize_keyboard=True,
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user.id,)
    )
    db.commit()

    await update.message.reply_text(
        f"🎉 Welcome to TaskNova BD!\n\n"
        f"Hello, {user.first_name}!\n"
        "Choose an option below.",
        reply_markup=keyboard,
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if text == "💰 Balance":
        row = db.execute(
            "SELECT balance FROM users WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        balance = row[0] if row else 0

        await update.message.reply_text(
            f"💰 Your balance: ৳{balance:.2f}"
        )

    elif text == "📋 Tasks":
        await update.message.reply_text(
            "📋 Available Tasks\n\n"
            "New tasks will be announced here.\n"
            "Please wait for the admin to add tasks."
        )

    elif text == "👥 Refer":
        bot = await context.bot.get_me()
        link = f"https://t.me/{bot.username}?start={user_id}"

        await update.message.reply_text(
            f"👥 Invite your friends!\n\n"
            f"Your referral link:\n{link}\n\n"
            "Referral rewards are not automatic yet."
        )

    elif text == "💳 Withdraw":
        await update.message.reply_text(
            "💳 To request a withdrawal, contact the bot admin.\n"
            "Payments are not automatic."
        )

    else:
        await update.message.reply_text(
            "Please select an option from the menu.",
            reply_markup=keyboard,
        )

async def admin_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "👑 TaskNova BD Admin Panel\n\n"
        "Bot is running successfully!"
    )

def main():
    if not TOKEN:
        raise ValueError("BOT_TOKEN is missing!")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin_help))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, menu)
    )

    print("TaskNova BD is running!")
    app.run_polling()

if __name__ == "__main__":
    main()
