import telegram
import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API key from environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Get Telegram bot token from environment variable
bot = telegram.Bot(token=os.environ.get("TELEGRAM_BOT_TOKEN"))

# Set default system prompt and temperature
system_prompt = "This is the default prompt."
temperature = 0.5

# Listen for messages
updates = bot.get_updates()
for update in updates:
    message = update.message
    chat_id = message.chat.id
    text = message.text

    # Check if user wants to change the system prompt
    if text.startswith("/system"):
        system_prompt = text.split("/system ")[1]
        bot.send_message(chat_id=chat_id, text=f"System prompt set to:\n{system_prompt}")
    # Check if user wants to change the temperature
    elif text.startswith("/temp"):
        temperature = float(text.split("/temp ")[1])
        bot.send_message(chat_id=chat_id, text=f"Temperature set to:\n{temperature}")
    else:
        # Pass message to GPT-3 and get response
        response = openai.Completion.create(
            engine="davinci-3.5-turbo",
            prompt=f"{system_prompt}\nUser: {text}\nSystem:",
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=temperature,
        ).choices[0].text

        # Send response back to user
        bot.send_message(chat_id=chat_id, text=response)