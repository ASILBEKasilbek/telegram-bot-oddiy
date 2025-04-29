import logging
from aiogram import Bot, Dispatcher
from filters import IsOwnerFilter, IsAdminFilter, MemberCanRestrictFilter
import config
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from throttling import ThrottlingMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)

# init
store = MemoryStorage()
bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot , storage=MemoryStorage())

# activate filters
dp.filters_factory.bind(IsOwnerFilter)
dp.filters_factory.bind(IsAdminFilter)
dp.filters_factory.bind(MemberCanRestrictFilter)
dp.middleware.setup(ThrottlingMiddleware())


# import logging
# from aiogram import Bot, Dispatcher
# from filters import IsOwnerFilter, IsAdminFilter, MemberCanRestrictFilter
# import config
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from throttling import ThrottlingMiddleware

# # Configure logging
# logging.basicConfig(level=logging.INFO)

# def setup_dispatcher(bot: Bot) -> Dispatcher:
#     """Berilgan bot uchun yangi Dispatcher yaratadi."""
#     dp = Dispatcher(bot, storage=MemoryStorage())

#     # Activate filters
#     dp.filters_factory.bind(IsOwnerFilter)
#     dp.filters_factory.bind(IsAdminFilter)
#     dp.filters_factory.bind(MemberCanRestrictFilter)

#     dp.middleware.setup(ThrottlingMiddleware())

#     return dp

# def create_bot_and_dispatcher(token: str):
#     """Yangi Bot va Dispatcher obyektlarini qaytaradi."""
#     bot = Bot(token=token, parse_mode="HTML")
#     dp = setup_dispatcher(bot)
#     return bot, dp
