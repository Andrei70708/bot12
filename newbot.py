# Import necessary modules
import os
import logging
import time
from aiogram import Bot, Dispatcher, executor, types
import openai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment variables
bot_token = os.getenv('BOT_TOKEN') # Bot token from Telegram API
api_key = os.getenv('API_KEY') # API key for OpenAI
chat_id = os.getenv('CHAT_ID') # ID of the chat where the bot will send messages

# Set up logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=bot_token)
dp = Dispatcher(bot)

# Set up OpenAI API key
openai.api_key = api_key

# Create a dictionary to store messages for each user
messages = {}

# Handle the /start command
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    try:
        username = message.from_user.username
    except AttributeError:
        await message.answer("Please set a username in Telegram settings and try again.")
        return
    messages[username] = []
    await message.answer("Hello, I'm bot powered on API GPT-3.5-turbo (ChatGPT)")

# Handle the /newtopic command
@dp.message_handler(commands=['newtopic'])
async def new_topic_cmd(message: types.Message):
    username = message.from_user.username
    messages[username] = []
    await message.answer("Created new chat!")

# Handle /setprompt command. Lets user set a new system prompt on the fly.
@dp.message_handler(commands=['setprompt'])
async def set_prompt_cmd(message: types.Message):
    username = message.from_user.username
    prompt = message.text.split(' ', 1)[1]
    messages[username] = []
    messages[username].append({"role": "system", "content": prompt})
    await message.answer(f"System prompt set to '{prompt}'.")

# Handle /settemperature command. Lets user set the temperature for the AI response.
@dp.message_handler(commands=['settemperature'])
async def set_temperature_cmd(message: types.Message):
    username = message.from_user.username
    temperature = message.text.split(' ', 1)[1]
    messages[username] = []
    messages[username].append({"role": "system", "content": f"Temperature set to {temperature}."})
    await message.answer(f"Temperature set to {temperature}.")

# Handle /setfreqpenalty command. Lets user set the frequency penalty for the AI response.
@dp.message_handler(commands=['setfreqpenalty'])
async def set_freq_penalty_cmd(message: types.Message):
    username = message.from_user.username
    freq_penalty = message.text.split(' ', 1)[1]
    messages[username] = []
    messages[username].append({"role": "system", "content": f"Frequency penalty set to {freq_penalty}."})
    await message.answer(f"Frequency penalty set to {freq_penalty}.")

# Handle /setprespenalty command. Lets user set the presence penalty for the AI response.
@dp.message_handler(commands=['setprespenalty'])
async def set_pres_penalty_cmd(message: types.Message):
    username = message.from_user.username
    pres_penalty = message.text.split(' ', 1)[1]
    messages[username] = []
    messages[username].append({"role": "system", "content": f"Presence penalty set to {pres_penalty}."})
    await message.answer(f"Presence penalty set to {pres_penalty}.")



# Handle all other messages
@dp.message_handler()
async def echo_msg(message: types.Message):
    user_message = message.text
    username = message.from_user.username

    # If this is the first message from the user, create a new list to store messages
    if username not in messages:
        messages[username] = []

    # Add user's message to the message list
    messages[username].append({"role": "user", "content": user_message})
    messages[username].append({"role": "system", "content": "You are a Helpful assistant."})

    # Log the user's message
    logging.info(f'{username}: {user_message}')

    # Check if this message is a reply to a previous message from the bot
    should_respond = not message.reply_to_message or message.reply_to_message.from_user.id == bot.id

    # If this is a new message or a message that the bot needs to respond to
    if should_respond:
        # Use OpenAI to generate a response
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages[username],
            max_tokens=1024,
            temperature=float(messages[username].get('temperature', '0.7')),
            frequency_penalty=float(messages[username].get('freq_penalty', '0')),
            presence_penalty=float(messages[username].get('pres_penalty', '0')),
            user=username
        )
        chatgpt_response = completion.choices[0]['message']
        messages[username].append({"role": "assistant", "content": chatgpt_response['content']})

        # Log the bot's response
        logging.info(f'ChatGPT response: {chatgpt_response["content"]}')

        # Send the bot's response to the chat
        await message.reply(chatgpt_response['content'], parse_mode='Markdown', chat_id=chat_id)



if __name__ == '__main__':
    # Send a greeting message with the current system time
    hello_message = f"Hello! I'm bot powered on API GPT-3.5-Turbo(ChatGPT). Here are your options:\n/newtopic - Create a new chat"
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    greeting_message = f"{hello_message}\n\n{current_time}"
    bot.send_message(chat_id=chat_id, text=greeting_message)
    #CLI Logging
    logging.info("Bot started at %s", time.strftime('%Y-%m-%d %H:%M:%S'))
    executor.start_polling(dp)
