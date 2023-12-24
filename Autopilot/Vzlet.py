# импорт используемых библиотек
import math
import time
import krpc
import os
import json


def log():
    global data
    current_ut = space_center.ut
    v = vessel.flight(vessel.orbit.body.reference_frame).vertical_speed
    vector_v_all = vessel.flight(vessel.orbit.body.reference_frame).velocity
    v_all = (vector_v_all[0] ** 2 + vector_v_all[1] ** 2 + vector_v_all[2] ** 2) ** 0.5
    h = vessel.flight(vessel.orbit.body.reference_frame).surface_altitude
    data.append([vessel.mass, h, v, v_all, current_ut])
    time.sleep(0.3)


# выставляем необходимые параметры орбиты
turn_start_altitude = 250
turn_end_altitude = 45000
target_altitude = 150000

# настраиваем соединение с сервером игры
conn = krpc.connect(name='Launch into orbit')

# получаем данные о корабле
vessel = conn.space_center.active_vessel
space_center = conn.space_center
tech_stage = 7
ut = conn.add_stream(getattr, conn.space_center, 'ut')
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
stage_resources = vessel.resources_in_decouple_stage(stage=tech_stage, cumulative=False)
stage_fuel = conn.add_stream(stage_resources.amount, 'LiquidFuel')

# настраиваем корабль перед взлетом
vessel.control.sas = False
vessel.control.rcs = False
vessel.control.throttle = 1.0
turn_angle = 0
data = []

# выводим обратный отсчет перед взлетом
print('3...')
time.sleep(1)
print('2...')
time.sleep(1)
print('1...')
time.sleep(1)
print('Взлет!')

# запуск двигателя
vessel.control.activate_next_stage()
vessel.auto_pilot.engage()
vessel.auto_pilot.target_pitch_and_heading(90, 90)

while True:

    # выполняем полное логирование полета
    log()

    # изменение угла поворота корабля при взлете
    if altitude() > turn_start_altitude and altitude() < turn_end_altitude:
        frac = ((altitude() - turn_start_altitude) /
                (turn_end_altitude - turn_start_altitude))
        new_turn_angle = frac * 90
        if abs(new_turn_angle - turn_angle) > 0.5:
            turn_angle = new_turn_angle
            vessel.auto_pilot.target_pitch_and_heading(90 - turn_angle, 90)

    # управление системой отсоединения ступеней
    if stage_fuel() < 0.1:
        vessel.control.activate_next_stage()
        tech_stage -= 1
        time.sleep(1)
        stage_resources = vessel.resources_in_decouple_stage(stage=tech_stage, cumulative=False)
        stage_fuel = conn.add_stream(stage_resources.amount, 'LiquidFuel')
        time.sleep(1)
        print('stage separated', tech_stage, stage_fuel())

    # выход из цикла в момент достижения высоты конца маневра
    if apoapsis() > target_altitude * 0.9:
        print('Approaching target apoapsis')
        break

vessel.control.throttle = 0.25
while apoapsis() < target_altitude:
    log()

vessel.control.throttle = 0.0

# ждем выхода из атмосферы
while altitude() < 70500:
    log()

# сохрание в файл логов взлета
with open("Data_vzlet", 'w', encoding="UTF-8") as file:
    json.dump(data, file, ensure_ascii=False, indent=2)

# проверка на то, что запись логов велась
if len(data) != 0:
    print("Лог взлета записан!")

# планирование маневра закругления орбиты
print('Planning circularization burn')
mu = vessel.orbit.body.gravitational_parameter
r = vessel.orbit.apoapsis
a1 = vessel.orbit.semi_major_axis
a2 = r
v1 = math.sqrt(mu * ((2. / r) - (1. / a1)))
v2 = math.sqrt(mu * ((2. / r) - (1. / a2)))
delta_v = v2 - v1
node = vessel.control.add_node(ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

# рассчитывание времения работы двигатель для выполнения маневра
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(delta_v / Isp)
flow_rate = F / Isp
burn_time = (m0 - m1) / flow_rate

# ориентация корабля для маневра
vessel.auto_pilot.reference_frame = node.reference_frame
vessel.auto_pilot.target_direction = (0, 1, 0)
vessel.auto_pilot.wait()

# запуск ускорения времени до старта манёвра
burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time / 2.)
lead_time = 5
conn.space_center.warp_to(burn_ut - lead_time)
time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
while time_to_apoapsis() - (burn_time / 2.) > 0:
    pass

# выполнение манёвра
vessel.control.throttle = 1.0
time.sleep(burn_time - 0.1)
vessel.control.throttle = 0.05
remaining_burn = conn.add_stream(node.remaining_burn_vector, node.reference_frame)
fl = True
while remaining_burn()[1] > 0.5:
    if stage_fuel() < 0.1:
        vessel.control.activate_next_stage()
        tech_stage -= 1
        time.sleep(1)
        stage_resources = vessel.resources_in_decouple_stage(stage=tech_stage, cumulative=False)
        stage_fuel = conn.add_stream(stage_resources.amount, 'LiquidFuel')
        time.sleep(1)
        fl = False
vessel.control.throttle = 0.0
node.remove()

# проверяем оставшееся топливо
if fl == True:
    vessel.control.activate_next_stage()
    vessel.control.activate_next_stage()

# закрываем соединение с сервером
conn.close()

# взел выполнен, запуск файла перелета на Муну
print("Взлет завершен!")
file = "Orbit_change.py"
os.system(f'python {file}')
