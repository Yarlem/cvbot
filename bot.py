#Блок загрузок сторонних модулей
from config import TOKEN
from config import api_key
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.utils import executor
from googleapiclient.discovery import build
import os
import googleapiclient.errors

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TOKEN)
storage=MemoryStorage()
dp = Dispatcher(bot, storage=storage)

#Создание кнопок с командами
k1 = KeyboardButton('/find')
k2 = KeyboardButton('/help')
k3 = KeyboardButton('/info')
k4 = KeyboardButton('/git')

hotkeys=ReplyKeyboardMarkup(resize_keyboard=True)
hotkeys.add(k1).insert(k2).add(k3).insert(k4)

#Установка состояний
class Form(StatesGroup):
    name = State()

#Парсинг json файла для получения нужных данных от Youtube
def saving(list):
    for i in list['items']:
        return(i['id']['videoId'])

YT = build('youtube', 'v3', developerKey=api_key)

#Команда для поиска
@dp.message_handler(commands=['find'], state=None)
async def find_command(message: types.Message):
    await Form.name.set()
    await message.reply('Что нужно найти?')

#Получение данных от пользователя
@dp.message_handler(state=Form.name)
async def get_object(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
        #Обработка запроса через API Youtube
    
    request = YT.search().list(part="snippet", maxResults=1, q=data['name'])
    response = request.execute()   
    ytlink = 'https://www.youtube.com/watch?v='+saving(response)
    await message.answer(ytlink)
    await state.finish()

#Установка команд для бота
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.answer('Привет! \nЭто бот-приложение к резюме. \nВведите /help для получения списка команд', reply_markup=hotkeys)

@dp.message_handler(commands=['help'])
async def help_command(message: types.Message):
    await message.answer('/find - ищет на Youtube ролик по названию. \nНапример: /find portugal the man feel it still')
    await message.answer('/info - для подробного описания целей этого бота')
    await message.answer('/git - для получения доступа к коду бота')

@dp.message_handler(commands=['info'])
async def info_command(message: types.Message):
    await message.answer('Бот создан, чтобы продемонстрировать навыки работы с API на примере работы с Telegram и Youtube. А так же понимание работы с Git, открытый доступ к коду позволяет оценить качество выполнения этого маленького проекта')

@dp.message_handler(commands=['git'])
async def git_command(message: types.Message):
    await message.answer('https://github.com/Yarlem/cvbot')

#Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
