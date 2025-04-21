import os

CARS_FILE = "cars.txt"
SALES_FILE = "sales.txt"
STATS_FILE = "stats.txt"

BANNER = """
🚗🚙🏎️  СИСТЕМА КЕРУВАННЯ АВТОПАРКОМ  🚓🚕🚘
-----------------------------------------
"""

MENU = """
1️⃣  ➕ Додати авто
2️⃣  📜 Переглянути авто
3️⃣  🔍 Пошук авто за маркою
4️⃣  💰 Фільтрація авто за ціною
5️⃣  ✏️ Редагувати авто
6️⃣  ❌ Видалити авто
7️⃣  💵 Продати авто
8️⃣  📜 Історія продажів
9️⃣  🔙 Відновити продане авто
🔟  🚀 Переглянути найдорожче авто
1️⃣1️⃣  📊 Зберегти статистику
0️⃣  🚪 Вихід
"""

def load_data(filename):
    """Завантаження даних з файлу"""
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as file:
        return [line.strip() for line in file.readlines()]

def save_data(filename, data):
    """Збереження даних у файл"""
    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(data) + "\n")

def add_car():
    """Додавання авто"""
    print("\n🚗 Додавання нового авто:")
    brand = input("Марка: ")
    model = input("Модель: ")
    year = input("Рік випуску: ")
    price = input("Ціна ($): ")

    cars = load_data(CARS_FILE)
    cars.append(f"{brand},{model},{year},{price}")
    save_data(CARS_FILE, cars)
    print(f"✅ Авто {brand} {model} додано!\n")

def view_cars():
    """Перегляд авто"""
    cars = load_data(CARS_FILE)
    if not cars:
        print("❌ Немає доступних авто.\n")
        return

    print("\n📜 Список авто:")
    for i, car in enumerate(cars, start=1):
        brand, model, year, price = car.split(",")
        print(f"{i}. {brand} {model} ({year}) - ${price}")
    print()

def search_car():
    """Пошук авто за маркою"""
    query = input("\n🔍 Введіть марку авто: ").lower()
    cars = load_data(CARS_FILE)
    results = [car for car in cars if car.lower().startswith(query)]
    
    if results:
        print("\n🔎 Знайдені авто:")
        for car in results:
            print(car.replace(",", " "))
    else:
        print("❌ Нічого не знайдено.\n")

def filter_by_price():
    """Фільтрація авто за ціною"""
    max_price = int(input("\n💰 Введіть максимальну ціну ($): "))
    cars = load_data(CARS_FILE)
    filtered = [car for car in cars if int(car.split(",")[3]) <= max_price]
    
    if filtered:
        print("\n💲 Авто у вашому ціновому діапазоні:")
        for car in filtered:
            print(car.replace(",", " "))
    else:
        print("❌ Немає авто у такій ціні.\n")

def edit_car():
    """Редагування авто"""
    view_cars()
    cars = load_data(CARS_FILE)
    index = int(input("\n✏️ Виберіть номер авто для редагування: ")) - 1

    if 0 <= index < len(cars):
        brand, model, year, price = cars[index].split(",")
        print(f"\nРедагування {brand} {model}:")

        brand = input(f"Нова марка ({brand}): ") or brand
        model = input(f"Нова модель ({model}): ") or model
        year = input(f"Новий рік ({year}): ") or year
        price = input(f"Нова ціна ({price}): ") or price

        cars[index] = f"{brand},{model},{year},{price}"
        save_data(CARS_FILE, cars)
        print("✅ Авто оновлено!\n")
    else:
        print("❌ Невірний вибір.\n")

def delete_car():
    """Видалення авто"""
    view_cars()
    cars = load_data(CARS_FILE)
    index = int(input("\n❌ Виберіть номер авто для видалення: ")) - 1

    if 0 <= index < len(cars):
        print(f"🚮 Авто {cars[index].replace(',', ' ')} видалено.")
        cars.pop(index)
        save_data(CARS_FILE, cars)
    else:
        print("❌ Невірний вибір.\n")

def sell_car():
    """Продаж авто"""
    view_cars()
    cars = load_data(CARS_FILE)
    sales = load_data(SALES_FILE)
    index = int(input("\n💵 Виберіть номер авто для продажу: ")) - 1

    if 0 <= index < len(cars):
        sold_car = cars.pop(index)
        sales.append(sold_car)
        save_data(CARS_FILE, cars)
        save_data(SALES_FILE, sales)
        print(f"✅ Авто продано: {sold_car.replace(',', ' ')}\n")
    else:
        print("❌ Невірний вибір.\n")

def view_sales():
    """Перегляд історії продажів"""
    sales = load_data(SALES_FILE)
    if not sales:
        print("❌ Продажів ще не було.\n")
        return

    print("\n📜 Історія продажів:")
    for sale in sales:
        print(sale.replace(",", " "))
    print()

def restore_sold_car():
    """Відновлення проданого авто"""
    sales = load_data(SALES_FILE)
    if not sales:
        print("❌ Немає проданих авто.\n")
        return

    view_sales()
    index = int(input("\n🔙 Виберіть номер авто для відновлення: ")) - 1

    if 0 <= index < len(sales):
        car = sales.pop(index)
        cars = load_data(CARS_FILE)
        cars.append(car)
        save_data(CARS_FILE, cars)
        save_data(SALES_FILE, sales)
        print(f"✅ Авто відновлено: {car.replace(',', ' ')}\n")
    else:
        print("❌ Невірний вибір.\n")

def main():
    while True:
        print(BANNER)
        print(MENU)
        choice = input("👉 Виберіть опцію: ")

        actions = {
            "1": add_car,
            "2": view_cars,
            "3": search_car,
            "4": filter_by_price,
            "5": edit_car,
            "6": delete_car,
            "7": sell_car,
            "8": view_sales,
            "9": restore_sold_car,
            "10": lambda: print("🚀 Показати найдорожче авто"),
            "11": lambda: print("📊 Зберегти статистику"),
            "0": exit
        }

        action = actions.get(choice)
        if action:
            action()
        else:
            print("❌ Невірний вибір.\n")

if __name__ == "__main__":
    main()
