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