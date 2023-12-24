import time
import json
import math
import krpc




# настраиваем соединение с сервером игры
conn = krpc.connect()

# получаем данные о корабле
space_center = conn.space_center
vessel = conn.space_center.active_vessel
data = []

# получение радиус-векторов позиции космического корабля и позиции Луны
distance_to_moon = 100000000000
space_center.rails_warp_factor = 5
min_dist = 10000000000000

# ожидания окна посадки
while distance_to_moon >= 100000:
    min_dist = min(min_dist, distance_to_moon)
    ship_position = space_center.active_vessel.position(space_center.active_vessel.orbit.body.reference_frame)
    moon_position = space_center.bodies["Mun"].position(space_center.active_vessel.orbit.body.reference_frame)
    distance_to_moon = ((moon_position[0] - ship_position[0]) ** 2 + (moon_position[1] - ship_position[1]) ** 2 + (
            moon_position[2] - ship_position[2]) ** 2) ** 0.5
    print(distance_to_moon, min_dist, "метров")
    if (distance_to_moon > min_dist):
        break
    time.sleep(2)
space_center.physics_warp_factor = 0

# настройка корабля для манёвра выравнивания орбиты Муны
vessel.control.sas_mode = vessel.control.sas_mode.retrograde
vessel.control.throttle = 1
time.sleep(2)
apoapsis_altitude = 10 ** 14
periapsis_altitude = 0

# выравнивание орбиты
while abs(periapsis_altitude - apoapsis_altitude) > 10 ** 6:
    vessel = space_center.active_vessel
    orbit = vessel.orbit
    apoapsis_altitude = orbit.apoapsis_altitude
    periapsis_altitude = orbit.periapsis_altitude
    time.sleep(1)
space_center.physics_warp_factor = 0

# отсоединяем ступень перед посадкой
vessel.control.activate_next_stage()
vessel.control.activate_next_stage()

print("Орбита луны успешно выровнена")
time.sleep(3)

################################################################################################################
# переход к посадке

# настройка корабля перед посадкой
vessel.control.sas_mode = vessel.control.sas_mode.retrograde

# получение орбиты посадки
pere_altitude = conn.get_call(getattr, vessel.orbit, 'periapsis_altitude')
expr = conn.krpc.Expression.less_than(
    conn.krpc.Expression.call(pere_altitude),
    conn.krpc.Expression.constant_double(-198000))
event = conn.krpc.add_event(expr)
vessel.control.throttle = 1

# ожидание выхода на орбиту посадки
with event.condition:
    event.wait()
vessel.control.throttle = 0
time.sleep(1)

# ускорение времени до высоты 25км
space_center.rails_warp_factor = 5
while vessel.flight(vessel.orbit.body.reference_frame).surface_altitude > 25000:
    time.sleep(0.1)
    continue
space_center.physics_warp_factor = 0

# ожидание высоты 21км
while vessel.flight(vessel.orbit.body.reference_frame).surface_altitude > 21000:
    time.sleep(0.1)
    continue


h = 1
V = 1

# запуск алгоритма получения высоты посадки и ожидания необходимой высоты
while h > 0 or V > 2:
    F = 60000
    cos_f = 1
    #k = 3.54
    k = 13
    m0 = vessel.mass
    h = vessel.flight(vessel.orbit.body.reference_frame).surface_altitude
    GM = 6.5138398 * 10 ** 10
    r = 200_000
    # dt = 0.1
    V = vessel.flight(vessel.orbit.body.reference_frame).vertical_speed
    dt = 0.01
    t = 0
    current_ut = space_center.ut

    # запись логов посадки
    data.append([m0, h, V, current_ut])

    time.sleep(0.1)
    while V < 0 and h > 0:
        t += 0.01
        dVy = ((F * cos_f) / (m0 - k * t) - GM / ((r + h) ** 2)) * dt
        V = V + dVy
        dh = V * dt
        h = h + dh

    print(h, V)

# запуск двигателя посадки
vessel.control.throttle = 1
vessel.control.legs = True

# финальная корректировка мягкой посадки

while vessel.flight(vessel.orbit.body.reference_frame).surface_altitude > 20:

    # запись логов посадки
    current_ut = space_center.ut
    v = vessel.flight(vessel.orbit.body.reference_frame).vertical_speed
    h = vessel.flight(vessel.orbit.body.reference_frame).surface_altitude
    data.append([vessel.mass, h, v, current_ut])
    time.sleep(0.1)

    if v < -12:
        vessel.control.throttle = 1
    elif v > -8:
        vessel.control.throttle = 0
        time.sleep(1)
    time.sleep(0.1)

# финальная корректировка мягкой посадки на высоте ниже 20 метров

while vessel.flight(vessel.orbit.body.reference_frame).surface_altitude > 5:

    # запись логов посадки
    current_ut = space_center.ut
    v = vessel.flight(vessel.orbit.body.reference_frame).vertical_speed
    h = vessel.flight(vessel.orbit.body.reference_frame).surface_altitude
    data.append([vessel.mass, h, v, current_ut])
    time.sleep(0.1)

    if v < -2:
        vessel.control.throttle = 0.25
    elif v > -2:
        vessel.control.throttle = 0
        time.sleep(1)
    time.sleep(0.1)
vessel.control.throttle = 0

# успешная посадка
print("Успешная посадка!")

# запись файлов логов
with open("Data_landing", 'w', encoding="UTF-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)

# закрываем соединение с сервером
conn.close()