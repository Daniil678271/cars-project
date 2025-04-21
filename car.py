import asyncio
import logging
import io
import random
import matplotlib.pyplot as plt
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Токен бота и файл базы данных
API_TOKEN = '7623216664:AAE4fwbBVtm450IPID3ZYUPcnWCUSHlI_Bc'
DB_FILE = 'cars_db.txt'

# Инициализация бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Месяцы для графиков
months = ["Nov 2024", "Dec 2024", "Jan 2025", "Feb 2025", "Mar 2025"]

# Цвета для графиков
COLORS = ['blue', 'green', 'red', 'purple', 'orange', 'cyan', 'magenta']

# Загрузка данных
def load_data():
    cars_data = {}
    price_history = {}
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as file:
            for line in file:
                if line.strip():
                    parts = line.strip().split(',')
                    logger.info(f"Parsing line: {parts}")
                    car_name = parts[0]
                    cars_data[car_name] = {
                        "price": int(parts[1]),
                        "horsepower": int(parts[2]),
                        "fuel_economy": parts[3],
                        "year": int(parts[4]),
                        "engine_type": parts[5] if len(parts) > 5 else "Unknown",
                        "country": parts[6] if len(parts) > 6 else "Unknown"
                    }
                    price_history[car_name] = [int(price) for price in parts[-1].split()]
                    if len(price_history[car_name]) != len(months):
                        logger.warning(f"Adjusting price history for {car_name}: {price_history[car_name]}")
                        price_history[car_name] = price_history[car_name] + [cars_data[car_name]['price']] * (len(months) - len(price_history[car_name]))
    except FileNotFoundError:
        logger.warning("File not found, initializing with default data")
        cars_data = {
            "Toyota Camry": {"price": 25000, "horsepower": 203, "fuel_economy": "28 MPG", "year": 2023, "engine_type": "Gasoline", "country": "Japan"},
            "Honda Civic": {"price": 22000, "horsepower": 158, "fuel_economy": "32 MPG", "year": 2023, "engine_type": "Gasoline", "country": "Japan"},
            "BMW X5": {"price": 60000, "horsepower": 335, "fuel_economy": "21 MPG", "year": 2023, "engine_type": "Diesel", "country": "Germany"},
            "Tesla Model 3": {"price": 45000, "horsepower": 283, "fuel_economy": "134 MPGe", "year": 2023, "engine_type": "Electric", "country": "USA"}
        }
        price_history = {
            car: [data['price']] * len(months) for car, data in cars_data.items()
        }
        save_data(cars_data, price_history)
    return cars_data, price_history

# Сохранение данных
def save_data(cars_data, price_history):
    with open(DB_FILE, 'w', encoding='utf-8') as file:
        for car_name in cars_data:
            car = cars_data[car_name]
            prices = ' '.join(map(str, price_history[car_name]))
            line = f"{car_name},{car['price']},{car['horsepower']},{car['fuel_economy']},{car['year']},{car['engine_type']},{car['country']},{prices}\n"
            file.write(line)

cars_data, price_history = load_data()

# Состояния FSM
class CarState(StatesGroup):
    waiting_for_car = State()
    waiting_for_compare_cars = State()
    waiting_for_graph_period = State()

# Создание графика
def create_price_graph(car_names, period=None):
    try:
        logger.info(f"Creating graph for cars: {car_names}, period: {period}")
        plt.figure(figsize=(12, 6))
        if period:
            display_months = months[-int(period):]
        else:
            display_months = months

        for i, car_name in enumerate(car_names):
            prices = price_history[car_name][-len(display_months):] if period else price_history[car_name]
            logger.info(f"Car: {car_name}, Prices: {prices}, Months: {display_months}")
            if not prices or len(prices) != len(display_months):
                logger.error(f"Invalid price data for {car_name}: {prices}")
                return None
            plt.plot(range(len(display_months)), prices, marker='o', label=car_name, color=COLORS[i % len(COLORS)])
        
        plt.xticks(range(len(display_months)), display_months, rotation=45)
        plt.title(f"Price Trend for {', '.join(car_names)}")
        plt.xlabel("Months")
        plt.ylabel("Price (USD)")
        plt.grid(True)
        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        plt.close()
        logger.info(f"Graph created successfully for {car_names}")
        return BufferedInputFile(buf.getvalue(), filename=f"{'_vs_'.join(car_names)}_price_graph.png")
    except Exception as e:
        logger.error(f"Error creating graph for {car_names}: {e}")
        return None

# Главное меню
@dp.message(F.text == "/start")
async def send_welcome(message: Message):
    kb = ReplyKeyboardBuilder()
    kb.add(types.KeyboardButton(text="Список машин"))
    kb.add(types.KeyboardButton(text="График цен"))
    kb.add(types.KeyboardButton(text="Характеристики"))
    kb.add(types.KeyboardButton(text="Сравнить машины"))
    await message.answer(
        "Привет! Я бот для анализа машин. Выбери опцию:",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )
    logger.info(f"User {message.from_user.id} started the bot")

# Список машин
@dp.message(F.text == "Список машин")
async def list_cars(message: Message):
    response = "Список машин и их стоимость:\n"
    for car, data in cars_data.items():
        response += f"{car}: ${data['price']}\n"
    await message.answer(response)
    logger.info(f"User {message.from_user.id} requested car list")

# Запрос графика
@dp.message(F.text == "График цен")
async def ask_for_car_graph(message: Message, state: FSMContext):
    kb = InlineKeyboardBuilder()
    for name in cars_data:
        kb.add(types.InlineKeyboardButton(text=name, callback_data=f"graph_{name}"))
    kb.add(types.InlineKeyboardButton(text="Сравнить несколько", callback_data="graph_compare"))
    kb.adjust(2)
    await message.answer("Выбери машину для графика цен или сравни несколько:", reply_markup=kb.as_markup())
    logger.info(f"User {message.from_user.id} requested price graph")

# Обработка выбора машины для графика
@dp.callback_query(F.data.startswith("graph_"))
async def process_car_graph_selection(callback: types.CallbackQuery, state: FSMContext):
    car_name = callback.data.replace("graph_", "")
    if car_name == "compare":
        await callback.message.answer("Выбери первую машину для сравнения:")
        kb = ReplyKeyboardBuilder()
        kb.add(types.KeyboardButton(text="/cancel"))
        for name in cars_data:
            kb.add(types.KeyboardButton(text=name))
        await callback.message.answer("Выбери машину:", reply_markup=kb.as_markup(resize_keyboard=True))
        await state.set_state(CarState.waiting_for_compare_cars)
        await state.update_data(cars=[])
    else:
        kb = InlineKeyboardBuilder()
        kb.add(types.InlineKeyboardButton(text="3 месяца", callback_data=f"period_3_{car_name}"))
        kb.add(types.InlineKeyboardButton(text="5 месяцев", callback_data=f"period_5_{car_name}"))
        kb.add(types.InlineKeyboardButton(text="Все месяцы", callback_data=f"period_all_{car_name}"))
        await callback.message.answer("Выбери период для графика:", reply_markup=kb.as_markup())
    await callback.answer()

# Выбор периода для графика
@dp.callback_query(F.data.startswith("period_"))
async def process_graph_period(callback: types.CallbackQuery):
    try:
        period, car_name = callback.data.replace("period_", "").split("_", 1)
        logger.info(f"Processing graph period: {period}, car: {car_name}")
        period = None if period == "all" else int(period)
        graph = create_price_graph([car_name], period)
        if graph:
            await bot.send_photo(
                callback.message.chat.id,
                photo=graph,
                caption=f"График цен для {car_name} за {'все время' if period is None else f'{period} месяцев'}"
            )
        else:
            await callback.message.answer("Не удалось создать график. Проверьте данные или попробуйте позже.")
    except Exception as e:
        logger.error(f"Error in process_graph_period: {e}")
        await callback.message.answer("Произошла ошибка при создании графика.")
    await callback.answer()

# Сравнение машин для графика
@dp.message(CarState.waiting_for_compare_cars)
async def process_compare_cars(message: Message, state: FSMContext):
    car_name = message.text
    if car_name == "/cancel":
        await message.answer("Действие отменено.", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
        return
    if car_name not in cars_data:
        await message.answer("Такой машины нет в списке. Попробуйте снова.")
        return
    data = await state.get_data()
    cars = data.get("cars", [])
    cars.append(car_name)
    if len(cars) < 2:
        await message.answer(f"Выбрано: {car_name}. Выбери вторую машину для сравнения:")
        await state.update_data(cars=cars)
    else:
        kb = InlineKeyboardBuilder()
        kb.add(types.InlineKeyboardButton(text="3 месяца", callback_data=f"compare_period_3_{'_'.join(cars)}"))
        kb.add(types.InlineKeyboardButton(text="5 месяцев", callback_data=f"compare_period_5_{'_'.join(cars)}"))
        kb.add(types.InlineKeyboardButton(text="Все месяцы", callback_data=f"compare_period_all_{'_'.join(cars)}"))
        kb.adjust(2)
        await message.answer("Выбери период для графика:", reply_markup=kb.as_markup())
        await state.update_data(cars=cars)

# Обработка периода для сравнения
@dp.callback_query(F.data.startswith("compare_period_"))
async def process_compare_graph_period(callback: types.CallbackQuery, state: FSMContext):
    try:
        period, car_names = callback.data.replace("compare_period_", "").split("_", 1)
        cars = car_names.split("_")
        period = None if period == "all" else int(period)
        graph = create_price_graph(cars, period)
        if graph:
            await bot.send_photo(
                callback.message.chat.id,
                photo=graph,
                caption=f"Сравнение цен для {', '.join(cars)} за {'все время' if period is None else f'{period} месяцев'}"
            )
        else:
            await callback.message.answer("Не удалось создать график. Проверьте данные или попробуйте позже.")
        await state.clear()
    except Exception as e:
        logger.error(f"Error in process_compare_graph_period: {e}")
        await callback.message.answer("Произошла ошибка при создании графика.")
    await callback.answer()

# Запрос характеристик
@dp.message(F.text == "Характеристики")
async def ask_for_car_specs(message: Message, state: FSMContext):
    kb = ReplyKeyboardBuilder()
    kb.add(types.KeyboardButton(text="/cancel"))
    for name in cars_data:
        kb.add(types.KeyboardButton(text=name))
    await message.answer("Выбери машину для характеристик:", reply_markup=kb.as_markup(resize_keyboard=True))
    await state.set_state(CarState.waiting_for_car)
    logger.info(f"User {message.from_user.id} requested car specs")

# Обработка характеристик
@dp.message(CarState.waiting_for_car)
async def process_car_specs(message: Message, state: FSMContext):
    car_name = message.text
    if car_name == "/cancel":
        await message.answer("Действие отменено.", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
        return
    if car_name not in cars_data:
        await message.answer("Такой машины нет в списке. Попробуйте снова!")
        return
    specs = cars_data[car_name]
    response = (
        f"Характеристики {car_name}:\n"
        f"Цена: ${specs['price']}\n"
        f"Мощность: {specs['horsepower']} л.с.\n"
        f"Экономия топлива: {specs['fuel_economy']}\n"
        f"Год выпуска: {specs['year']}\n"
        f"Тип двигателя: {specs['engine_type']}\n"
        f"Страна: {specs['country']}"
    )
    await message.answer(response)
    await state.clear()
    logger.info(f"User {message.from_user.id} viewed specs for {car_name}")

# Сравнение характеристик
@dp.message(F.text == "Сравнить машины")
async def ask_for_compare_specs(message: Message, state: FSMContext):
    await message.answer("Выбери первую машину для сравнения:")
    kb = ReplyKeyboardBuilder()
    kb.add(types.KeyboardButton(text="/cancel"))
    for name in cars_data:
        kb.add(types.KeyboardButton(text=name))
    await message.answer("Выбери машину:", reply_markup=kb.as_markup(resize_keyboard=True))
    await state.set_state(CarState.waiting_for_compare_cars)
    await state.update_data(cars=[])
    logger.info(f"User {message.from_user.id} requested car comparison")

# Обработка сравнения характеристик
@dp.message(CarState.waiting_for_compare_cars)
async def process_compare_specs(message: Message, state: FSMContext):
    car_name = message.text
    if car_name == "/cancel":
        await message.answer("Действие отменено.", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
        return
    if car_name not in cars_data:
        await message.answer("Такой машины нет в списке. Попробуйте снова.")
        return
    data = await state.get_data()
    cars = data.get("cars", [])
    cars.append(car_name)
    if len(cars) < 2:
        await message.answer(f"Выбрано: {car_name}. Выбери вторую машину для сравнения:")
        await state.update_data(cars=cars)
    else:
        car1, car2 = cars
        specs1, specs2 = cars_data[car1], cars_data[car2]
        response = (
            f"Сравнение {car1} и {car2}:\n\n"
            f"{car1}:\n"
            f"Цена: ${specs1['price']} | {car2}: ${specs2['price']}\n"
            f"Мощность: {specs1['horsepower']} л.с. | {car2}: {specs2['horsepower']} л.с.\n"
            f"Экономия топлива: {specs1['fuel_economy']} | {car2}: {specs2['fuel_economy']}\n"
            f"Год: {specs1['year']} | {car2}: {specs2['year']}\n"
            f"Тип двигателя: {specs1['engine_type']} | {car2}: {specs2['engine_type']}\n"
            f"Страна: {specs1['country']} | {car2}: {specs2['country']}"
        )
        await message.answer(response)
        await state.clear()
        logger.info(f"User {message.from_user.id} compared {car1} and {car2}")

# Отмена
@dp.message(F.text == "/cancel")
async def cancel_action(message: Message, state: FSMContext):
    await message.answer("Действие отменено.", reply_markup=types.ReplyKeyboardRemove())
    await state.clear()
    logger.info(f"User {message.from_user.id} cancelled action")

# Основной запуск
async def main():
    print("✅ Бот запущен. Ожидаем команды...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("⛔ Бот остановлен.")