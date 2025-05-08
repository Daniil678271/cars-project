distant = int(input("Введи длину трасы в километрах:"))
speed = 120
fuel_consumpption = 10
tank_fuel = 50
time = 5/60
s = (distant / 100) * fuel_consumpption 
pit_stops = int(s // tank_fuel)
used = s% tank_fuel
a = tank_fuel - used if s > tank_fuel else tank_fuel - s
driving_time = distant / speed
total_time = driving_time + (pit_stops * time)

print(f"Количество пит-стопов: {pit_stops}")
print(f"Общее время гонки: {total_time:.2f} часов")
print(f"Остаток топлива: {a} литров")