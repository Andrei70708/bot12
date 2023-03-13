import os
import logging
import time
from aiogram import Bot, Dispatcher, executor, types
import openai
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

bot_token = os.getenv('BOT_TOKEN')
api_key = os.getenv('API_KEY')
chat_id = os.getenv('CHAT_ID')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=bot_token)
dp = Dispatcher(bot)

openai.api_key = api_key

messages = {}


@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    try:
        username = message.from_user.username
    except AttributeError:
        await message.answer("Please set a username in Telegram settings and try again.")
        return
    messages[username] = []
    await message.answer("Hello, I'm bot powered on API GPT-3.5-turbo (ChatGPT)")


@dp.message_handler(commands=['newtopic'])
async def new_topic_cmd(message: types.Message):
    username = message.from_user.username
    messages[username] = []
    await message.answer("Created new chat!")


@dp.message_handler()
async def echo_msg(message: types.Message):
    user_message = message.text
    username = message.from_user.username

    if username not in messages:
        messages[username] = []
    messages[username].append({"role": "user", "content": user_message})
    messages[username].append({"role": "system", "content": "You are a Helpful assistant."})
    #messages[username].append({"role": "user", "content": f"chat: {message.chat} It's {time.strftime('%d/%m/%Y %H:%M:%S')} user: {message.from_user.first_name} message: {message.text}"})
    logging.info(f'{username}: {user_message}')

    should_respond = not message.reply_to_message or message.reply_to_message.from_user.id == bot.id

    if should_respond:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages[username],
            max_tokens=1024,
            temperature=0.7,
            frequency_penalty=0,
            presence_penalty=0,
            user=username
        )
        chatgpt_response = completion.choices[0]['message']
        messages[username].append({"role": "assistant", "content": chatgpt_response['content']})
        logging.info(f'ChatGPT response: {chatgpt_response["content"]}')
        await message.reply(chatgpt_response['content'], parse_mode='Markdown', chat_id=chat_id)


if __name__ == '__main__':
    # Send a greeting message with the current system time
    hello_message = f"Hello! I'm bot powered on API GPT-3.5-Turbo(ChatGPT). Here are your options:\n/newtopic - Create a new chat"
    current_time = time.strftime('%Y-%m-%d %H:%M:%S')
    greeting_message = f"{hello_message}\n\n{current_time}"
    bot.send_message(chat_id=CHAT_ID, text=greeting_message)
    #CLI Logging
    logging.info("Bot started at %s", time.strftime('%Y-%m-%d %H:%M:%S'))
    executor.start_polling(dp)
