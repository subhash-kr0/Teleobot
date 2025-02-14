import os
import logging
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Load environment variables
load_dotenv()

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "deepseek/deepseek-r1:free"

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Dictionary to store conversation history
user_conversations = {}

async def start(update: Update, context: CallbackContext):
    """Send welcome message when /start is issued"""
    user_id = update.message.chat_id
    user_conversations[user_id] = []  # Initialize conversation for the user

    await update.message.reply_text(
        "🤖 Hello! I'm an AI assistant powered by OpenRouter. Ask me anything!\n\n"
        f"⚙️ Current model: {DEFAULT_MODEL}"
    )

async def handle_message(update: Update, context: CallbackContext):
    """Handle incoming messages and generate responses using OpenRouter"""
    try:
        user_id = update.message.chat_id
        user_message = update.message.text

        # Maintain conversation history (last 5 messages)
        if user_id not in user_conversations:
            user_conversations[user_id] = []
        user_conversations[user_id].append({"role": "user", "content": user_message})
        user_conversations[user_id] = user_conversations[user_id][-5:]  # Keep last 5 messages

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "HTTP-Referer": "https://github.com/subhash-kr0",  
            "X-Title": "Your Bot Name",
        }

        payload = {
            "model": DEFAULT_MODEL,
            "messages": user_conversations[user_id],
            "temperature": 0.7,
            "max_tokens": 500  # Reduce token usage for efficiency
        }

        # Make API request to OpenRouter
        response = requests.post(OPENROUTER_URL, json=payload, headers=headers)
        response.raise_for_status()
        
        # Extract and send response
        ai_response = response.json()['choices'][0]['message']['content']

        # Store AI response in conversation history
        user_conversations[user_id].append({"role": "assistant", "content": ai_response})
        user_conversations[user_id] = user_conversations[user_id][-5:]  # Keep last 5 messages

        await update.message.reply_text(ai_response)

    except Exception as e:
        logger.error(f"Error processing message: {e}")
        await update.message.reply_text("⚠️ Sorry, I encountered an error processing your request.")

def main():
    """Start the bot"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    logger.info("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()


