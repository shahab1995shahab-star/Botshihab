import os
from openai import OpenAI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

async def start(update: Update, context):
    await update.message.reply_text("أهلاً! أنا بوت DeepSeek. اسألني أي شيء.")

async def reply(update: Update, context):
    msg = update.message.text
    res = client.chat.completions.create(
        model="deepseek-v4-flash",
        messages=[{"role": "user", "content": msg}]
    )
    await update.message.reply_text(res.choices[0].message.content)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    app.run_polling()

if __name__ == "__main__":
    main()