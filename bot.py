import logging
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InputFile
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def StartBot():
    with open("token.txt", 'r', encoding='utf-8') as f:
        API_TOKEN = f.readline()
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot)
    async def RaspChoice(message: types.Message):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Расписание занятий", url="https://rasp.omgtu.ru/ruz/main"))
        keyboard.add(types.InlineKeyboardButton(text="График учебного процесса",
                                                url="https://omgtu.ru/students/grafik_uchebnogo_protsessa.php"))
        keyboard.add(types.InlineKeyboardButton(text="Расписание консультаций",
                                                url="https://omgtu.ru/general_information/departments/education_and_methodical/the-schedule-of-consultations/"))
        keyboard.add(types.InlineKeyboardButton(text="В меню", callback_data="rasp_back"))
        await message.answer("Выберите вариант из списка", reply_markup=keyboard)

    @dp.callback_query_handler(text=["rasp_back"])
    async def rasp_messages(call: types.CallbackQuery):
        if call.data == "rasp_back":
            await MenuChoise(call.message)
        await call.answer()

    def GetFaculties():
        URL = "https://omgtu.ru/general_information/faculties/"
        html_code = requests.get(URL)
        soup = BeautifulSoup(html_code.content, 'html.parser')
        pagecontent_div = soup.find('div', {'id': 'pagecontent'})
        a_elements = pagecontent_div.find_all('ul')[0].find_all('a')
        result = {}
        for a in a_elements:
            href = a.get('href')
            try:
                text = a.find('span').text
            except:
                text = a.text
            result[text] = href
        print(result)
        return result

    async def FacultiesChoice(message: types.Message):
        FacList = GetFaculties()
        keyboard = types.InlineKeyboardMarkup()
        for text, link in FacList.items():
            keyboard.add(types.InlineKeyboardButton(text=text, url=link))
        await message.answer("Выберите факультет из списка", reply_markup=keyboard)

    async def MenuChoise(message: types.Message):
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton(text="Расписание", callback_data="menu_rasp"))
        keyboard.add(types.InlineKeyboardButton(text="Информация о факультетах", callback_data="menu_faculties"))
        keyboard.add(
            types.InlineKeyboardButton(text="Оплата обучения и общежитий", url="https://omgtu.ru/students/pay/"))
        keyboard.add(types.InlineKeyboardButton(text="Группа ОмГТУ ВКонтакте", url="https://vk.com/omskpoliteh"))
        await message.answer("Что подсказать?.", reply_markup=keyboard)

    @dp.callback_query_handler(text=["menu_map", "menu_rasp", "menu_faculties"])
    async def menu_messages(call: types.CallbackQuery):
        if call.data == "menu_rasp":
            await RaspChoice(call.message)
        elif call.data == "menu_faculties":
            await FacultiesChoice(call.message)
        await call.answer()

    @dp.message_handler(commands=['start', 'help'])
    async def send_welcome(message: types.Message):
        await message.answer("Приветствую, путник. Видимо ты заблудился. Я помогу тебе освоиться.")
        await MenuChoise(message)

    executor.start_polling(dp, skip_updates=True)
