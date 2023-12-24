import numpy as np
import matplotlib.pyplot as plt
import math
import json

with open("Data_landing2.json", encoding="UTF-8") as file_in:
    records = json.load(file_in)

vs2 = []
ti2 = []
hg2 = []
ms2 = []
for data in records:
    t2 = data[3] - 509516.0003508733
    ves2 = data[2] * (-1)
    m2 = data[0]
    h2 = data[1]
    ti2.append(t2)
    vs2.append(ves2)
    hg2.append(h2)
    ms2.append(m2)


F = 60000
cos_f = 0.88294759
k = 17.734
m0 = 3212.04541015625
h = 20992
GM = 6.5138398*10**10
r = 200_000
V = -608
dt = 0.1
t = 0
m = m0
ti = []
vs = []
hg = []
ms = []
def turbo(V,h,tg,m):
    l_ti = []
    l_ms = []
    l_vs = []
    l_hg = []
    t = 0
    while V < 0 and h > 0:
        l_ti.append(tg + t)
        t += 0.1
        l_ms.append(m)
        m = m0 - k * t
        dVy = (F / m - GM / ((r + h) ** 2))*dt
        l_vs.append((-1) * V)
        V = V + dVy
        dh = V * dt
        l_hg.append(h)
        h = h + dh
    if (-20 <= V <= 20) and  (-20 <= h <= 20):
        ti.extend(l_ti)
        ms.extend(l_ms)
        vs.extend(l_vs)
        hg.extend(l_hg)
        print(1111111)
        return True
    return False

while h >= 0:
    ti.append(t)
    t += 0.1
    ms.append(m)
    dVy = (- GM / ((r + h) ** 2)) * dt
    V = V + dVy
    dh = V * dt
    vs.append((-1) * V)
    h = h + dh
    hg.append(h)

    if turbo(V, h, t, m):
        print(11)
        break

plt.title("Посадка" + '\n' + "Зависимость высоты от времени")
plt.xlabel("Время, с")
plt.ylabel("Высота, м")
plt.plot(ti2, hg2, label='KSP')
plt.plot(ti, hg, color="red", label='Мат Модель')
plt.legend()
plt.grid(True)
plt.show()