# -*- coding: utf-8 -*-

import asyncio
from app.handlers import router
from bot_dp import bot, dp
from app.database.models import async_main


async def main():
    print('Бот запущен')
    try:
        await async_main()
        dp.include_router(router)
        await dp.start_polling(bot)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
