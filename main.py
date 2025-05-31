from datetime import datetime, timezone
import requests
from telegram import Bot
import time
from dotenv import load_dotenv
import os
import asyncio
import random

load_dotenv()

NASA_API = os.getenv("NASA_API")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
LAST_POSTED_FILE = 'last.txt'

def read_last_posted():
    if not os.path.exists(LAST_POSTED_FILE):
        return None
    with open(LAST_POSTED_FILE, 'r') as file:
        return file.read().strip()
    
def write_last_posted(post_id):
    with open(LAST_POSTED_FILE, 'w') as file:
        file.write(post_id)

def get_apod():
    url = f'https://api.nasa.gov/planetary/apod?api_key={NASA_API}'
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        post_id = data.get('date')
        return {
            "id": post_id,
            "type": "apod",
            "title": data.get("title"),
            "explanation": data.get("explanation"),
            "url": data.get("url")
        }
    else:
        print("Failed to get APOD:", res.status_code)
        return None

def get_epic():
    url = f'https://api.nasa.gov/EPIC/api/natural/images?api_key={NASA_API}'
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        if not data:
            print("No Epic Images found")
            return None
        
        image_data = random.choice(data)
        image_name = image_data['image']
        date_str = image_data['date'].split()[0]
        year, month, day = date_str.split('-')
        image_url = f"https://epic.gsfc.nasa.gov/archive/natural/{year}/{month}/{day}/jpg/{image_name}.jpg"
        title = f'EPIC Earth Image from {date_str}'
        explanation = "A photo taken by NASA's EPIC camera on the DSCOVR satellite."

        return {
            "id": image_url,  # use URL as unique ID
            "type": "epic",
            "title": title,
            "explanation": explanation,
            "url": image_url
        }
    else:
        print("Failed to get EPIC:", res.status_code)
        return None

def select_nasa_image():
    if random.choice([True, False]):
        return get_apod()
    else:
        return get_epic()

async def post_to_channel(bot, data):
    title = data['title']
    explanation = data['explanation']
    image_url = data['url']

    message = f"<b>{title}</b>\n\n{explanation}"
    await bot.send_photo(chat_id=CHANNEL_ID, photo=image_url, caption=title, parse_mode="HTML")
    await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode='HTML')

async def main():
    bot = Bot(token=BOT_TOKEN)
    last_posted = read_last_posted()
    today = datetime.now(timezone.utc).date().isoformat()
    nasa_data = select_nasa_image()
    
    if not nasa_data:
        print("No data received from NASA")
        return

    if nasa_data['id'] == last_posted:
        print("Already posted this image")
        return

    await post_to_channel(bot, nasa_data)
    write_last_posted(nasa_data['id'])
    print(f"Posted: {nasa_data['title']}")

if __name__ == '__main__':
    asyncio.run(main())
