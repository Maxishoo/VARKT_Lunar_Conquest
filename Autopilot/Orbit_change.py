import time
import os
import krpc
import math


# настраиваем соединение с сервером игры
conn = krpc.connect()

# получаем данные о корабле
space_center = conn.space_center
vessel = conn.space_center.active_vessel

# настраиваем корабль
vessel.control.sas = True
vessel.control.sas_mode = vessel.control.sas_mode.prograde
time.sleep(0.5)

# включаем глобальное ускорение времени
space_center.rails_warp_factor = 10

# ждем пока угол между луной и кораблем не будет необходимым
k = 0
while True:
    ship_position = space_center.active_vessel.position(space_center.active_vessel.orbit.body.reference_frame)
    moon_position = space_center.bodies["Mun"].position(space_center.active_vessel.orbit.body.reference_frame)
    v1 = [ship_position[0], ship_position[1], ship_position[2]]
    v2 = [moon_position[0], moon_position[1], moon_position[2]]
    cosfi = (v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2]) / (
            ((v1[0] ** 2 + v1[1] ** 2 + v1[2] ** 2) ** 0.5) * ((v2[0] ** 2 + v2[1] ** 2 + v2[2] ** 2) ** 0.5))
    if cosfi > -0.8 and cosfi < -0.76:
        k += 1
        time.sleep(0.5)
    if k >= 2:
        break

space_center.physics_warp_factor = 0

# выполняем разгон до необходимой скорости
print("Начало разгона")

# настройка корабля перед разгоном
vessel.control.sas_mode = vessel.control.sas_mode.prograde
vessel.control.throttle = 1
dv = space_center.active_vessel.orbit.speed + 800

# разгон
while space_center.active_vessel.orbit.speed < dv:
    print(space_center.active_vessel.orbit.speed, dv)
    time.sleep(0.1)

# конец разгона
vessel.control.throttle = 0

# закрываем соединение с сервером
conn.close()

# выводим сообщение о том, что ракета вышла на необходимую траекторию
print("fil swaped")

# запускаем файл перелета и посадки на Муну
file = "Transfer_and_landing.py"
os.system(f'python {file}')
