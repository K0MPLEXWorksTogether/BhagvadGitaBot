import logging
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, CallbackContext
from data import getVerseData, getAudioData, deleteAudioFile
from user import query, create, delete
import datetime

import os
import aiohttp
from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context: CallbackContext) -> None:
    """Sends a greeting and explains the bot functionality"""
    message = (
        "Hello! I'm a Bhagavad Gita bot.\n\n"
        "Here are the commands you can use:\n"
        "/start - Greet the user and explain bot functionality.\n"
        "/verse <chapter> <verse> - Get a specific verse from the Bhagavad Gita.\n"
        "/daily <order> <time> - Schedule an action based on your preferences.\n\n"
        "To get a verse, use /verse followed by the chapter and verse numbers.\n"
        "To schedule something, use /daily with either 'random' or 'sequential' order and a time."
    )
    await update.message.reply_text(message)


async def verse(update: Update, context: CallbackContext) -> None:
    """Fetches and returns a verse from the Bhagavad Gita"""
    try:
        chapter = context.args[0]
        verse = context.args[1]

        verseData = getVerseData(chapter=chapter, verse=verse)
        print(f"Got verse data for {chapter}, {verse}.")
        audioData = getAudioData(chapter=chapter, verse=verse)
        print(f"Got audio data for {chapter}, {verse}.")

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

        if len(message) > 4096:
            while len(message) > 4096:
                await update.message.reply_text(message[:4096])
                message = message[4096:]
            await update.message.reply_text(message)  # Send the remaining part of the message
        else:
            await update.message.reply_text(message, parse_mode="Markdown")
        
        
        print(f"Sent verse data for {chapter}, {verse}.")

        audioFilePath = os.path.join(audioData, f"{chapter}-{verse}.mp3")
        if os.path.exists(audioFilePath):
            with open(audioFilePath, "rb") as audioFile:
                await update.message.reply_audio(audio=InputFile(audioFile), caption=f"Audio Recital For Chapter {chapter}, Verse {verse}.")
                print(f"sent audio data for {chapter}, {verse}.")
        else:
            await update.message.reply_text(f"Sorry, the audio for Chapter {chapter}, Verse {verse} is not available.")
            print(f"Could not send audio data for {chapter}, {verse}.")

    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /verse <chapter> <verse>")
        logger.error(f"There was a usage error for {chapter}, {verse}.")

    except Exception as VerseError:
        logger.error(f"There was an unexpected error for {chapter}, {verse}: {VerseError}")

    deleteAudioFile(chapter, verse)

async def daily(update: Update, context: CallbackContext) -> None:
    """Processes the order and time for scheduling"""
    try:
        if len(context.args) != 2:
            await update.message.reply_text("Usage: /daily <order> <time>")
            return

        order = context.args[0]
        time_str = context.args[1]

        if order not in ['random', 'sequential']:
            await update.message.reply_text("Order must be either 'random' or 'sequential'.")
            return
        
        try:
            time_obj = datetime.datetime.strptime(time_str, "%H:%M")
            time = time_obj.strftime("%H:%M")
        except ValueError:
            await update.message.reply_text("Time should be in 24-hour format (HH:MM).")
            return


        if update.message is None:
            await update.message.reply_text("Error: No message found in the update.")
            return  

        username = update.message.from_user.username
        chatId = str(update.message.chat_id)

        async with aiohttp.ClientSession() as session:
            usertype = await query(session, username)

            if usertype == "does not exist":
                success = await create(session, username=username, usertype=order, chatID=chatId, time=time)
                if not success:
                    await update.message.reply_text("Failed to create scheduling. Try again later.")
                    return
            elif usertype in ["random", "sequential"]:
                deleteSuccess = await delete(session, username=username, usertype=usertype)
                if not deleteSuccess:
                    await update.message.reply_text("Failed to delete the previous schedule. Try again later.")
                    return 

                create_success = await create(session, username=username, usertype=order, chatID=chatId, time=time)
                if not create_success:
                    await update.message.reply_text("Failed to create new scheduling. Try again later.")
                    return
            else:
                await update.message.reply_text(f"Request to schedule verse in {order} failed due to an internal server error. Try again.")
                return
            
            await update.message.reply_text(f"Request to schedule {order} order at {time_str} received.")

    except (IndexError, ValueError):
        await update.message.reply_text("Usage: /daily <order> <time>")
    except Exception as e:
        print(f"Unexpected error: {e}")
        await update.message.reply_text("An unexpected error occurred. Please try again later.")

async def error(update: Update, context: CallbackContext) -> None:
    """Logs errors caused by updates"""
    logger.warning(f"Update {update} caused error {context.error}")

def main() -> None:
    """Start the bot"""
    # Replace 'YOUR_TOKEN' with your bot's token
    application = Application.builder().token(os.getenv("BOT_TOKEN")).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("verse", verse))
    application.add_handler(CommandHandler("daily", daily))

    application.add_error_handler(error)
    application.run_polling(poll_interval=5)

if __name__ == '__main__':
    main()
