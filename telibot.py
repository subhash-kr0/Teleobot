from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
import openai

class Reference:
    """
    A class to store previous responses from the chatGPT API.
    """
    def __init__(self) -> None:
        self.response = ""

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

reference = Reference()
TOKEN = os.getenv("BOT_TOKEN")

# Model name
MODEL_NAME = "gpt-4o-mini"

# Initialize bot and router
bot = Bot(token=TOKEN)
router = Router()  # Aiogram 3.x uses Router for handlers
dp = Dispatcher()

def clear_past():
    """Clear the previous conversation and context."""
    reference.response = ""

@router.message(Command("start"))
async def welcome(message: Message):
    """
    This handler receives messages with the `/start` command.
    """
    await message.answer("Hi\nI am Tele Bot!\nCreated by Bappy. How can I assist you?")

@router.message(Command("clear"))
async def clear(message: Message):
    """
    A handler to clear the previous conversation and context.
    """
    clear_past()
    await message.answer("I've cleared the past conversation and context.")

@router.message(Command("help"))
async def helper(message: Message):
    """
    A handler to display the help menu.
    """
    help_command = (
        "Hi there, I'm a chatGPT Telegram bot created by Bappy!\n"
        "Please follow these commands:\n"
        "/start - Start the conversation\n"
        "/clear - Clear the past conversation and context\n"
        "/help - Display this help menu\n"
        "I hope this helps. :)"
    )
    await message.answer(help_command)

@router.message(F.text)
async def chatgpt(message: Message):
    """
    A handler to process the user's input and generate a response using the chatGPT API.
    """
    print(f"USER: {message.text}")
    try:
        response = openai.ChatCompletion.create(
            model=MODEL_NAME,
            messages=[
                {"role": "assistant", "content": reference.response},
                {"role": "user", "content": message.text},
            ]
        )
        reference.response = response['choices'][0]['message']['content']
        print(f"chatGPT: {reference.response}")
        await message.answer(reference.response)
    except Exception as e:
        error_message = "An error occurred while processing your request. Please try again later."
        print(f"Error: {e}")
        await message.answer(error_message)

async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)  # Ensures no old updates interfere
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
