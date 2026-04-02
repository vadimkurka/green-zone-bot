"""Post Green Zone picks to Telegram channel."""
import asyncio
import logging
from aiogram import Bot
from aiogram.enums import ParseMode
from config import BOT_TOKEN, CHANNEL_ID
from odds_fetcher import get_green_zone_picks
from formatter import format_picks_message

logging.basicConfig(level=logging.INFO)

async def main():
    bot = Bot(token=BOT_TOKEN)
    try:
        picks = await get_green_zone_picks()
        messages = format_picks_message(picks)
        for msg in messages:
            await bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode=ParseMode.HTML)
            await asyncio.sleep(1)
        print(f"Posted {len(picks)} picks")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
