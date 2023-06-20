from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, Updater, CommandHandler, CallbackContext, CallbackQueryHandler, ContextTypes
from bs4 import BeautifulSoup
import requests
import logging
from telegram.constants import ChatAction
import random
import re

# 1. BeautifulSoup: Use the command "pip install beautifulsoup4" to install this library.
# 2. Requests: Use the command "pip install requests" to install this library. So on and so forth....
# requirements: python3.9, PTB20.1.....


"""this file is specifically for fetching Japanese sentences containing the word you want on Aozora"""

"""Note: There are at least 4 things you need to edit in this file:
1. YOUR_BOT_TOKEN_HERE,
2. IDs_OF_THE_USERS_ALLOWED_TO_USE_THE_BOT,
3. https://www.aozora.gr.jp/cards/001383/files/56642_59575.html
4. https://www.aozora.gr.jp/cards/000148/files/789_14547.html
you should replace them with the ones you want"""

# Create a dictionary to store the results for each user
# This is necessary because Telegram is asynchronous and we need to maintain state between messages
user_data = {}

logging.basicConfig(
    # filename='logAtome.txt',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
# Set up Telegram bot
token = 'YOUR_BOT_TOKEN_HERE'
allowed_user_ids = [IDs_OF_THE_USERS_ALLOWED_TO_USE_THE_BOT]



async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    message_id = update.message.message_id
    if user_id not in allowed_user_ids:
        await context.bot.send_message(chat_id=chat_id, text="Hello! You can't use me because you are not a registered user yet! 👀", reply_to_message_id=message_id, parse_mode='HTML')
    else:
        await context.bot.send_message(chat_id=chat_id, text="Hello! You are a registered user! 🤝 Send me a command (/u, /y) followed by a Japanese word and I will fetch sentences containing the word from two books for you.\n\nUsage: /u <word> or /y <word>\n(u represents 『陰翳礼讃』; y represents 『吾輩は猫である』)\n\nSend /set_timer for more fun!", reply_to_message_id=message_id)



import httpx

async def word_lookup_u(update: Update, context: CallbackContext) -> None:
    """Handle the word lookup command."""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    if user_id in allowed_user_ids:
        command, word = update.message.text.split(' ', 1)  # Split the command and the word
        word = word.strip()
        # Get the webpage and parse it
        async with httpx.AsyncClient() as client:
            response = await client.get("https://www.aozora.gr.jp/cards/001383/files/56642_59575.html")
            response_content = response.content.decode('shift_jis')
            soup = BeautifulSoup(response_content, 'html.parser')
            ## Replace <ruby> text with <rb> text + <rt> text
            for ruby in soup.find_all('ruby'):
                rb = ruby.find('rb')
                rt = ruby.find('rt')
                if rb and rt:  # Ensure both tags are present
                    rb_text = rb.get_text(strip=True)
                    rt_text = rt.get_text(strip=True)
                    ruby.replace_with(f'{rb_text}({rt_text})')
            html_str = soup.get_text()
            # Find all sentences containing the word
            if word.lower() == "yoji":
                # Find all sentences containing 四字熟語
                sentences = [s for s in re.split(r'(?<=[。！？])', html_str) if re.search(r'[一-龯]{4}', s)]
            elif word.lower() == "abab":
                # Find all sentences containing ABAB pattern words
                sentences = [s for s in re.split(r'(?<=[。！？])', html_str) if re.search(r'([ァ-ヶ]{2})\1', s)]
            else:
                # Find all sentences containing the word
                sentences = [s for s in re.split(r'(?<=[。！？])', html_str) if word in s]
            if sentences:
                index_u = random.randint(0, len(sentences) - 1)  # Choose a random index
            else:
                index_u = 0
            user_data[user_id] = {word: {'sentences_u': sentences, 'index_u': index_u, 'page_url_u': response.url}}
            # Prepare the keyboard
            keyboard = [
            [
                InlineKeyboardButton("◀️Previous", callback_data=f'{user_id}:previous:{word}:lookup_u'),
                InlineKeyboardButton("🐥More Info/No", callback_data=f'{user_id}:more:{word}:lookup_u'),
                InlineKeyboardButton("Next▶️", callback_data=f'{user_id}:next:{word}:lookup_u'),
            ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            # Send a random sentence if it exists
            if sentences:
                sentence = sentences[index_u]
                await update.message.reply_text(sentence, reply_markup=reply_markup)
            else:
                await update.message.reply_text("No sentences found containing the word.")
    else:
        await context.bot.send_message(chat_id=chat_id, text="Sorry, you are not a registered user")

async def word_lookup_v(update: Update, context: CallbackContext) -> None:
    """Handle the second word lookup command."""
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    if user_id in allowed_user_ids:
        command, word = update.message.text.split(' ', 1)  # Split the command and the word
        word = word.strip()
        # Get the webpage and parse it
        async with httpx.AsyncClient() as client:
            response = await client.get("https://www.aozora.gr.jp/cards/000148/files/789_14547.html")
            response_content = response.content.decode('shift_jis')
            soup = BeautifulSoup(response_content, 'html.parser')
            # Replace <ruby> text with <rb> text + <rt> text
            for ruby in soup.find_all('ruby'):
                rb = ruby.find('rb')
                rt = ruby.find('rt')
                if rb and rt:  # Ensure both tags are present
                    rb_text = rb.get_text(strip=True)
                    rt_text = rt.get_text(strip=True)
                    ruby.replace_with(f'{rb_text}({rt_text})')
            html_str = soup.get_text()
            # Find all sentences containing the word
            if word.lower() == "yoji":
                # Find all sentences containing 四字熟語
                sentences = [s for s in re.split(r'(?<=[。！？])', html_str) if re.search(r'[一-龯]{4}', s)]
            elif word.lower() == "abab":
                # Find all sentences containing ABAB pattern words
                sentences = [s for s in re.split(r'(?<=[。！？])', html_str) if re.search(r'([ァ-ヶ]{2})\1', s)]
            else:
                # Find all sentences containing the word
                sentences = [s for s in re.split(r'(?<=[。！？])', html_str) if word in s]
            if sentences:
                index_v = random.randint(0, len(sentences) - 1)  # Choose a random index
            else:
                index_v = 0
            user_data[user_id] = {word: {'sentences_v': sentences, 'index_v': index_v, 'page_url_v': response.url}}
            # Prepare the keyboard
            keyboard = [
            [
                InlineKeyboardButton("◀️Previous", callback_data=f'{user_id}:previous:{word}:lookup_v'),
                InlineKeyboardButton("🐥More Info/No", callback_data=f'{user_id}:more:{word}:lookup_v'),
                InlineKeyboardButton("Next▶️", callback_data=f'{user_id}:next:{word}:lookup_v'),
            ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            # Send a random sentence if it exists
            if sentences:
                sentence = sentences[index_v]
                await update.message.reply_text(sentence, reply_markup=reply_markup)
            else:
                await update.message.reply_text("No sentences found containing the word.")
    else:
        await context.bot.send_message(chat_id=chat_id, text="Sorry, you are not a registered user")

async def word_lookup_u_timer(context: CallbackContext) -> None:
    chat_id, word, user_id = context.job.data
    # Get the webpage and parse it
    async with httpx.AsyncClient() as client:
        response = await client.get("https://www.aozora.gr.jp/cards/001383/files/56642_59575.html")
        response_content = response.content.decode('shift_jis')
        soup = BeautifulSoup(response_content, 'html.parser')
        # Replace <ruby> text with <rb> text + <rt> text
        for ruby in soup.find_all('ruby'):
            rb = ruby.find('rb')
            rt = ruby.find('rt')
            if rb and rt:  # Ensure both tags are present
                rb_text = rb.get_text(strip=True)
                rt_text = rt.get_text(strip=True)
                ruby.replace_with(f'{rb_text}({rt_text})')
        html_str = soup.get_text()
        # Find all sentences containing the word
        if word.lower() == "yoji":
            # Find all sentences containing 四字熟語
            sentences = [s for s in re.split(r'(?<=[。！？])', html_str) if re.search(r'[一-龯]{4}', s)]
        elif word.lower() == "abab":
            # Find all sentences containing ABAB pattern words
            sentences = [s for s in re.split(r'(?<=[。！？])', html_str) if re.search(r'([ァ-ヶ]{2})\1', s)]
        else:
            # Find all sentences containing the word
            sentences = [s for s in re.split(r'(?<=[。！？])', html_str) if word in s]
        if sentences:
            index_u = random.randint(0, len(sentences) - 1)  # Choose a random index
        else:
            index_u = 0
        user_data[user_id] = {word: {'sentences_u': sentences, 'index_u': index_u, 'page_url_u': response.url}}
        # Prepare the keyboard
        keyboard = [
        [
            InlineKeyboardButton("◀️Previous", callback_data=f'{user_id}:previous:{word}:lookup_u'),
            InlineKeyboardButton("🐥More Info/No", callback_data=f'{user_id}:more:{word}:lookup_u'),
            InlineKeyboardButton("Next▶️", callback_data=f'{user_id}:next:{word}:lookup_u'),
        ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Send a random sentence if it exists
        if sentences:
            sentence = sentences[index_u]
            await context.bot.send_message(chat_id=context.job.chat_id, text=sentence, reply_markup=reply_markup)
        else:
            await context.bot.send_message(chat_id=context.job.chat_id, text="No sentences found containing the word.")

async def word_lookup_v_timer(context: CallbackContext) -> None:
    chat_id, word, user_id = context.job.data
    # Get the webpage and parse it
    async with httpx.AsyncClient() as client:
        response = await client.get("https://www.aozora.gr.jp/cards/000148/files/789_14547.html")
        response_content = response.content.decode('shift_jis')
        soup = BeautifulSoup(response_content, 'html.parser')
        # Replace <ruby> text with <rb> text + <rt> text
        for ruby in soup.find_all('ruby'):
            rb = ruby.find('rb')
            rt = ruby.find('rt')
            if rb and rt:  # Ensure both tags are present
                rb_text = rb.get_text(strip=True)
                rt_text = rt.get_text(strip=True)
                ruby.replace_with(f'{rb_text}({rt_text})')
        html_str = soup.get_text()
        # Find all sentences containing the word
        if word.lower() == "yoji":
            # Find all sentences containing 四字熟語
            sentences = [s for s in re.split(r'(?<=[。！？])', html_str) if re.search(r'[一-龯]{4}', s)]
        elif word.lower() == "abab":
            # Find all sentences containing ABAB pattern words
            sentences = [s for s in re.split(r'(?<=[。！？])', html_str) if re.search(r'([ァ-ヶ]{2})\1', s)]
        else:
            # Find all sentences containing the word
            sentences = [s for s in re.split(r'(?<=[。！？])', html_str) if word in s]
        if sentences:
            index_v = random.randint(0, len(sentences) - 1)  # Choose a random index
        else:
            index_v = 0
        user_data[user_id] = {word: {'sentences_v': sentences, 'index_v': index_v, 'page_url_v': response.url}}
        # Prepare the keyboard
        keyboard = [
        [
            InlineKeyboardButton("◀️Previous", callback_data=f'{user_id}:previous:{word}:lookup_v'),
            InlineKeyboardButton("🐥More Info/No", callback_data=f'{user_id}:more:{word}:lookup_v'),
            InlineKeyboardButton("Next▶️", callback_data=f'{user_id}:next:{word}:lookup_v'),
        ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Send a random sentence if it exists
        if sentences:
            sentence = sentences[index_v]
            await context.bot.send_message(chat_id=context.job.chat_id, text=sentence, reply_markup=reply_markup)
        else:
            await context.bot.send_message(chat_id=context.job.chat_id, text="No sentences found containing the word.")




async def set_Timer_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends explanation on how to use the bot."""
    chat_id = update.effective_message.chat_id
    user_id = update.effective_message.from_user.id
    message_id = update.message.message_id
    if user_id not in allowed_user_ids:
        await context.bot.send_message(chat_id=chat_id, text="Hello! You can't set the timer because you are not a registered user yet! 👀", reply_to_message_id=message_id, parse_mode='HTML')
    else:
        await update.message.reply_text("Hi!\nUse /set_timer_u <seconds> <word> to set a timer for Ineiraisan\nUse /set_timer_y <seconds> <word> to set a timer for Wagahaineko\n\nFor example, send the following to make the bot fetch and send a random sentence containing the word 友人 every 100 minutes (i.e. 6000 seconds) from the webpage:\n/set_timer_u 6000 友人\n\n(After setting up the timer job, you could also send /unset_u, /unset_y to cancel it!)")


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    if context.job_queue is None:
        return False
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    return True

async def set_timer_u(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    user_id = update.effective_message.from_user.id
    user_data['id'] = update.effective_message.from_user.id
    message_id = update.message.message_id
    if user_id not in allowed_user_ids:
        await context.bot.send_message(chat_id=chat_id, text="Hello! You can't set the timer because you are not a registered user yet! 👀", reply_to_message_id=message_id, parse_mode='HTML')
    else:
        try:
            # args[0] should contain the time for the timer in seconds
            due = float(context.args[0])
            word = context.args[1]
            print(word)
            if due < 0:
                await update.effective_message.reply_text("Sorry we can not go back to future!")
                return
            job_removed = remove_job_if_exists(str(chat_id) + "Ineiraisan", context)
            if context.job_queue is None:
                await update.effective_message.reply_text("Job queue is not available")
            for i in range(365):
                context.job_queue.run_once(word_lookup_u_timer, due*i, chat_id=chat_id, name=str(chat_id) + "Ineiraisan", data=(chat_id, word, user_id))
            text = "Timer for Ineiraisan successfully set!"
            if job_removed:
                text += " Old one for Ineiraisan was removed."
            await update.effective_message.reply_text(text)
        except (IndexError, ValueError):
            await update.effective_message.reply_text("Usage: /set_timer_u <seconds> <word>")

async def set_timer_v(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Add a job to the queue."""
    chat_id = update.effective_message.chat_id
    user_id = update.effective_message.from_user.id
    user_data['id'] = update.effective_message.from_user.id
    message_id = update.message.message_id
    if user_id not in allowed_user_ids:
        await context.bot.send_message(chat_id=chat_id, text="Hello! You can't set the timer because you are not a registered user yet! 👀", reply_to_message_id=message_id, parse_mode='HTML')
    else:
        try:
            # args[0] should contain the time for the timer in seconds
            due = float(context.args[0])
            word = context.args[1]
            print(word)
            if due < 0:
                await update.effective_message.reply_text("Sorry we can not go back to future!")
                return
            job_removed = remove_job_if_exists(str(chat_id) + "Wagahaineko", context)
            if context.job_queue is None:
                await update.effective_message.reply_text("Job queue is not available")
            for i in range(365):
                context.job_queue.run_once(word_lookup_v_timer, due*i, chat_id=chat_id, name=str(chat_id) + "Wagahaineko", data=(chat_id, word, user_id))
            text = "Timer for Wagahaineko successfully set!"
            if job_removed:
                text += " Old one for Wagahaineko was removed."
            await update.effective_message.reply_text(text)
        except (IndexError, ValueError):
            await update.effective_message.reply_text("Usage: /set_timer_v <seconds> <word>")

async def unset_u(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id)+"Ineiraisan", context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)

async def unset_v(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Remove the job if the user changed their mind."""
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id)+"Wagahaineko", context)
    text = "Timer successfully cancelled!" if job_removed else "You have no active timer."
    await update.message.reply_text(text)

async def handle_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    callback_data = query.data.split(':')
    user_id = int(callback_data[0])
    action = callback_data[1]
    word = callback_data[2]
    command = callback_data[3]
    if user_id != query.from_user.id:
        # Ignore the callback query if it's from a different user
        await query.answer("No data available.")
        return
    # Get user data
    user_info = user_data.get(user_id)
    if not user_info or word not in user_info:
        await query.answer("No data available.")
        return
    # Distinguish the handling code based on the command
    if command == 'lookup_u':
        # Get user data
        user_info = user_data.get(user_id)
        if not user_info or word not in user_info:
            await query.answer("No data available.")
            return
        # Get current index, sentences, and page URL
        index = user_info[word].get('index_u')
        sentences = user_info[word].get('sentences_u')
        page_url = user_info[word].get('page_url_u')
    elif command == 'lookup_v':
        # Get user data
        user_info = user_data.get(user_id)
        if not user_info or word not in user_info:
            await query.answer("No data available.")
            return
        # Get current index, sentences, and page URL
        index = user_info[word].get('index_v')
        sentences = user_info[word].get('sentences_v')
        page_url = user_info[word].get('page_url_v')
    else:
        await query.answer("Invalid command.")
        return
    # Prepare the keyboard
    keyboard = [
        [
            InlineKeyboardButton("◀️Previous", callback_data=f'{user_id}:previous:{word}:{command}'),
            InlineKeyboardButton("🐥More Info/No", callback_data=f'{user_id}:more:{word}:{command}'),
            InlineKeyboardButton("Next▶️", callback_data=f'{user_id}:next:{word}:{command}'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if action == 'previous':
        if index > 0:
            index -= 1
        else:
            await query.answer("This is the first sentence.")
            return
    elif action == 'next':
        if index < len(sentences) - 1:
            index += 1
        else:
            await query.answer("This is the last sentence.")
            return
    elif action == 'more':
        if query.message.text.startswith("More Info:"):
            await query.edit_message_text(text=sentences[index], reply_markup=reply_markup)
            return
        else:
            await query.edit_message_text(
                text=f"More Info:\n{page_url}\n\nSentence {index+1} of {len(sentences)}",
                reply_markup=reply_markup
            )
            return
    # Update the index in the user data
    if command == 'lookup_u':
        user_data[user_id][word]['index_u'] = index
    elif command == 'lookup_v':
        user_data[user_id][word]['index_v'] = index
    await query.edit_message_text(text=sentences[index], reply_markup=reply_markup)







def main() -> None:
    """Start the bot."""
    application = ApplicationBuilder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("u", word_lookup_u))
    application.add_handler(CommandHandler("y", word_lookup_v))
    application.add_handler(CallbackQueryHandler(handle_callback))
    application.add_handler(CommandHandler("set_timer", set_Timer_help))
    application.add_handler(CommandHandler("set_timer_u", set_timer_u))
    application.add_handler(CommandHandler("set_timer_y", set_timer_v))
    application.add_handler(CommandHandler("unset_u", unset_u))
    application.add_handler(CommandHandler("unset_y", unset_v))
    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()
