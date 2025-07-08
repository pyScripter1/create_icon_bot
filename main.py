import requests  # Для отправки HTTP-запросов
import io  # Для работы с байтовыми потоками
from PIL import Image  # Для обработки изображений
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile
import asyncio
import random

# Вставьте ваш токен сюда
API_TOKEN_BOT = "Your_token"

# Текст на старте
INTRODUCE_TEXT = """Привет, я MyAvatar - сервис для мгновенной генерации прикольных аватарок.
Могу создать аватар на любой вкус и стиль. Выбери стиль и получи желаемую аватарку! 🤗"""
# Название картинки при старте
PIC_NAME = "introduce_pic.PNG"
# Общее количество страниц
TOTAL_PAGES = 5
BUTTONS_PER_PAGE = 6

styles = [
        "adventurer", "adventurer-neutral", "avataaars", "avataaars-neutral", "big-ears", "big-ears-neutral",
        "big-smile", "bottts", "bottts-neutral", "croodles", "croodles-neutral", "dylan", "fun-emoji", "glass",
        "icons", "identicon", "initials", "lorelei", "lorelei-neutral", "micah", "miniavs", "notionists",
        "notionists-neutral", "open-peeps", "personas", "pixel-art", "pixel-art-neutral", "rings", "shapes", "thumbs"
    ]

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN_BOT)
dp = Dispatcher()

# Создание клавиатуры с кнопками
def create_keyboard(page):
    # Создаем пустой список для строк кнопок
    inline_keyboard = []


    # Создаем кнопки для текущей страницы
    start_index = (page - 1) * BUTTONS_PER_PAGE
    end_index = page * BUTTONS_PER_PAGE
    buttons = []
    for style in styles[start_index:end_index]:
        buttons.append(InlineKeyboardButton(text=f"{style}", callback_data=f"style_{style}"))

    # Разбиваем кнопки по рядам (по 2 кнопки в ряду)
    for i in range(0, len(buttons), 2):
        inline_keyboard.append(buttons[i:i + 2])

    # Добавляем кнопки "Назад" и "Далее"
    navigation_buttons = []
    if page > 1:
        navigation_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"page_{page - 1}"))
    if page < TOTAL_PAGES:
        navigation_buttons.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"page_{page + 1}"))

    if navigation_buttons:
        inline_keyboard.append(navigation_buttons)

    # Создаем объект клавиатуры
    keyboard = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return keyboard

# Обработчик команды /start
@dp.message(Command("start"))
async def start_bot(message: types.Message):
    await message.answer(INTRODUCE_TEXT)
    await message.answer("Выберите стиль из списка ниже:", reply_markup=create_keyboard(1))
# Обработчик нажатия на кнопку
@dp.callback_query()
async def handle_callback(callback_query: types.CallbackQuery):
    print(f"Кнопка нажата", callback_query.data)
    data = callback_query.data

    if data.startswith("page_"):
        # Обработка нажатия на кнопку "Назад" или "Далее"
        page = int(data.split('_')[-1])
        try:
            await callback_query.message.edit_text(
                text=f"Выберите стиль из списка ниже: 📄 Страница {page}",
                reply_markup=create_keyboard(page)
            )
            await callback_query.answer()  # Подтверждаем обработку запроса
        except Exception as e:
            print(f"Ошибка при редактировании сообщения: {e}")
            await callback_query.answer("Не удалось переключить страницу.", show_alert=True)

    elif data.startswith("style_"):
        # Обработка выбора стиля
        style = data.split('_')[-1]
        await callback_query.answer(f"Вы выбрали стиль: {style}")  # Подтверждаем обработку
        # Генерация аватара
        user_seed = str(random.random())
        avatar = generate_dicebear_avatar(seed=user_seed, style=style)
        if avatar:
            # Сохраняем изображение во временный файл
            with io.BytesIO() as image_buffer:
                avatar.save(image_buffer, format="PNG")
                image_buffer.seek(0)
                # Преобразуем BytesIO в BufferedInputFile
                input_file = BufferedInputFile(image_buffer.getvalue(), filename="avatar.png")
                # Отправляем фото с клавиатурой
                await bot.send_photo(
                    chat_id=callback_query.message.chat.id,
                    photo=input_file,
                    caption=f"Аватар в стиле: {style}"
                )
                # Отправляем новое сообщение со списком стилей
                await bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text="Выберите стиль из списка ниже:",
                    reply_markup=create_keyboard(1)
                )

# Функция для отправки запроса и генерации изображения
def generate_dicebear_avatar(seed, style="identicon", size=1000):
    url = f"https://api.dicebear.com/9.x/{style}/png?seed={seed}&size={size}"
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        image_data = io.BytesIO(response.content)
        image = Image.open(image_data)
        return image
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе Dicebear API: {e}")
        return None
    except Exception as e:
        print(f"Ошибка при обработке изображения: {e}")
        return None

async def main():
    await dp.start_polling(bot)

# Запуск бота
if __name__ == "__main__":
    asyncio.run(main())
