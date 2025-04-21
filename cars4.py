cars = [["Ferrari", 500, 250000], ["Lexus", 349, 450000], ["BMW", 625, 110000]]

budchet = int(input("Бюджет:"))
total_spend_money = 0
total_power = 0
cars2 = []


for car in cars:
    tuned_cars = car[2] // 2
    if total_spend_money + tuned_cars <= budchet:
        cars2.append(f"{cars[0]}(Тюнинг: ${tuned_cars})")
        total_spend_money += tuned_cars
        total_power += car[1] * 1.2

print("Можно тюнинговать:",",".join(cars2))
print(f"Общая мощность после тюнинга: {round(total_power)} л.с")
print(f"Остаток бюджета: ${budchet - total_spend_money}")