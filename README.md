# Use-Telegram-bot-to-fetch-sentences-from-Aozora
This code file is specifically designed for fetching Japanese sentences from Aozora that contain the word you want via a Telegram bot.

"""Note: You need to edit at least 4 things in this file:
1. YOUR_BOT_TOKEN_HERE: replace it with your Bot Token.
2. IDs_OF_THE_USERS_ALLOWED_TO_USE_THE_BOT: you can modify the list of user IDs allowed to use the bot.
3. https://www.aozora.gr.jp/cards/001383/files/56642_59575.html: replace this link with the link to the page containing the desired word for the example sentences.
4. https://www.aozora.gr.jp/cards/000148/files/789_14547.html: replace this link with the link to the page for the desired word in another article on Aozora.
"""

# Requirements: Python 3.9, PTB 20.1.....

# Functions & Features: (note that in the example file, u represents the Aozora webpage of the book 『陰翳礼讃』, y represents the Aozora webpage of the book 『吾輩は猫である』)

1. Usage of the commands /u and /y
   
Send the bot a command (/u, /y) followed by a Japanese word and it will fetch sentences containing the word from two books for you: /u <word> or /y <word>

2. Usage of the commands /set_timer_u and /set_timer_y
   
Use /set_timer_u <seconds> <word> to set a timer for Ineiraisan
Use /set_timer_y <seconds> <word> to set a timer for Wagahaineko
For example, send the following to make the bot fetch and send a random sentence containing the word 友人 every 100 minutes (i.e. 6000 seconds) from the webpage:
/set_timer_u 6000 友人
(After setting up the timer job, you could also send /unset_u, /unset_y to cancel it!)

3. Feature: /u yoji; /y yoji; /set_timer_u yoji; /set_timer_y_yoji

A way to fetch 四字熟語! (it also fetches sentences that contain 4 consecutive Chinese characters with no other symbols in between)

4. Feature: /u abab; /y abab; /set_timer_u abab; /set_timer_y abab

A way to fetch words that have a ABAB pattern, like ピカピカ、ドキドキ!
