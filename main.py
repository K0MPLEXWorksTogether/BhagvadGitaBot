import logging
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, CallbackContext
from data import getVerseData, getAudioData, deleteAudioFile
import datetime

import os
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Handler for the /start command
async def start(update: Update, context: CallbackContext) -> None:
    """Sends a greeting and explains the bot functionality"""
    message = (
        "Hello! I'm a Bhagavad Gita bot.\n\n"
        "Here are the commands you can use:\n"
        "/start - Greet the user and explain bot functionality.\n"
        "/verse <chapter> <verse> - Get a specific verse from the Bhagavad Gita.\n"
        "/send <order> <time> - Schedule an action based on your preferences.\n\n"
        "To get a verse, use /verse followed by the chapter and verse numbers.\n"
        "To schedule something, use /send with either 'random' or 'sequential' order and a time."
    )
    await update.message.reply_text(message)

# Handler for the /verse command
async def verse(update: Update, context: CallbackContext) -> None:
    """Fetches and returns a verse from the Bhagavad Gita"""
    try:
        # Extract chapter and verse from the command arguments
        chapter = context.args[0]
        verse = context.args[1]

        verseData = getVerseData(chapter=chapter, verse=verse)
        audioData = getAudioData(chapter=chapter, verse=verse)

        original_verse = f"**{verseData['originalVerse']}**"
        transliteration = verseData["transliteration"]
        translation = verseData["translation"]
        commentary = verseData["commentary"]
        word_meanings = verseData["wordMeanings"]

        message = (
            f"**Original Verse:**\n"
            f"{original_verse}\n\n"
            f"**Transliteration:**\n"
            f"{transliteration}\n\n"
            f"**Translation:**\n"
            f"{translation}\n\n"
            f"**Commentary:**\n"
            f"{commentary}\n\n"
            f"**Word Meanings:**\n"
            f"{word_meanings}"
        )

        audioFilePath = os.path.join(audioData, f"{chapter}-{verse}.mp3")

        await update.message.reply_text(message, parse_mode="Markdown")

        if os.path.exists(audioFilePath):
            with open(audioFilePath, "rb") as audioFile:
                await update.message.reply_audio(audio=InputFile(audioFile), caption=f"Audio Recital For Chapter {chapter}, Verse {verse}.")
        else:
            await update.message.reply_text(f"Sorry, the audio for Chapter {chapter}, Verse {verse} is not available.")

        deleteAudioFile(chapter, verse)

    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /verse <chapter> <verse>")

    except Exception as VerseError:
        logger.error(f"There was an unexpected error for {chapter}, {verse}.")
        await update.message.reply_text("I faced a unexpected error. Try again after some time.")

# Handler for the /send command
async def send(update: Update, context: CallbackContext) -> None:
    """Processes the order and time for scheduling"""
    try:
        # Extract order and time from the command arguments
        order = context.args[0]
        time_str = context.args[1]

        # Check if the order is either 'random' or 'sequential'
        if order not in ['random', 'sequential']:
            await update.message.reply_text("Order must be either 'random' or 'sequential'.")
            return
        
        # Parse the time into a 24-hour format (this part is just for demonstration)
        try:
            time_obj = datetime.datetime.strptime(time_str, "%H:%M")
        except ValueError:
            await update.message.reply_text("Time should be in 24-hour format (HH:MM).")
            return
        
        # Acknowledge the request (you will handle database storage and logic)
        await update.message.reply_text(f"Request to schedule {order} order at {time_str} received.")

        # Add to your database here
        # Example: save_order_to_database(order, time_obj)

    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /send <order> <time>")

# Error handler for the bot
async def error(update: Update, context: CallbackContext) -> None:
    """Logs errors caused by updates"""
    logger.warning(f"Update {update} caused error {context.error}")

def main() -> None:
    """Start the bot"""
    # Replace 'YOUR_TOKEN' with your bot's token
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    # Register the commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verse", verse))
    application.add_handler(CommandHandler("send", send))

    # Log all errors
    application.add_error_handler(error)

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
