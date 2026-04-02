import asyncio
import logging
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram.enums import ParseMode

from config import BOT_TOKEN, CHANNEL_ID, FETCH_INTERVAL
from odds_fetcher import get_green_zone_picks
from formatter import format_picks_message

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "🟢 <b>GREEN ZONE BOT</b>\n\n"
        "Автоматические пики на спорт с вероятностью 80%+\n\n"
        "Формат:\n"
        "📊 Odds (American / European)\n"
        "🎯 Implied Probability\n"
        "📖 Bookmaker\n\n"
        "Подпишись на канал, чтобы получать пики каждые 4 часа.",
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("post"))
async def cmd_manual_post(message: Message, bot: Bot):
    """Manual trigger for testing."""
    await message.answer("⏳ Загружаю пики...")
    await post_picks_to_channel(bot)
    await message.answer("✅ Готово — проверяй канал.")


async def post_picks_to_channel(bot: Bot):
    """Fetch picks and post to channel."""
    try:
        picks = await get_green_zone_picks()
        messages = format_picks_message(picks)

        for msg in messages:
            await bot.send_message(
                chat_id=CHANNEL_ID,
                text=msg,
                parse_mode=ParseMode.HTML,
            )
            await asyncio.sleep(1)

        logger.info(f"Posted {len(picks)} picks in {len(messages)} messages")
    except Exception as e:
        logger.error(f"Error posting picks: {e}")


async def scheduler(bot: Bot):
    """Post picks every FETCH_INTERVAL seconds."""
    while True:
        logger.info("⏰ Scheduled fetch starting...")
        await post_picks_to_channel(bot)
        logger.info(f"Next fetch in {FETCH_INTERVAL} seconds")
        await asyncio.sleep(FETCH_INTERVAL)


async def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN not set")
    if not CHANNEL_ID:
        raise ValueError("CHANNEL_ID not set")

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    # Delete old webhooks
    await bot.delete_webhook(drop_pending_updates=True)

    # Start scheduler in background
    asyncio.create_task(scheduler(bot))

    logger.info("🟢 Green Zone Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
