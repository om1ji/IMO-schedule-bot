import asyncio
from common import dp, bot
import main_handler
from xl_parser import Group, Schedule, dump_data_to_pickle
from settings import pickle_file

dp.include_routers(main_handler.router)


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    dump_data_to_pickle()
    asyncio.run(main())
    # print(main_handler.get_schedule("04.3-208 (а)", "Понедельник", pickle_file))