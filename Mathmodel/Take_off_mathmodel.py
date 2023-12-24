import math
import matplotlib.pyplot as plt
import json

dataV=[]
dataH=[]
dataM=[]
dataT=[]
data=[]
with open("Data_vzlet2.json", encoding="UTF-8") as file_in:
    data = json.load(file_in)

for i in data:
    dataM.append(i[0])
    dataH.append(i[1])
    dataV.append(i[2])
    dataT.append(int(i[-1] - data[0][-1]))
    if dataH[-1]>70_000:
        break

F = 660_000
angle = 0

start_h = 250
end_h = 45_000
h = 250
GM = 3.5316000 * (10 ** 12)
r = 600_000
Vy = 0
dt = 0.01
tg = 0
tl = 0

m1 = 3533
m1_b = 2033
m2 = 2789
m2_b = 790
m3 = 10_690
m3_b = 2690
m4 = 30_840
m4_b = 6840
m0 = m1 + m2 + m3 + m4

k = (m4 - m4_b) / 100
p0 = 1
H = 5000
e = 2.71828

ti = []
vs = []
hg = []
ms = []
teck_stupen = 4

print(k)
def minus_stupen():
    global m0, m4, m4_b, m3, m3_b, m2, m2_b
    global m, k, F, tl, teck_stupen, h, tg

    if m < m0 - (m4 - m4_b) and teck_stupen == 4:
        m0 = m - m4_b
        F = 30_000
        tl=0
        k = 70
        teck_stupen -= 1
   
jj=0
cos_f = 1
while h < 70000:
    if h > start_h and h < end_h:
        frac = (h - start_h) / (end_h - start_h)
        new_angle = frac * 90.0
        if abs(new_angle - angle) > 0.5:
            angle = new_angle
        cos_f = math.cos(angle)

    m = m0 - k * tl
    minus_stupen()
    ms.append(m)
    ti.append(tg)
    tl += 0.01
    tg += 0.01
    cos_f =1
    A = 0.008 * m
    d = 0.2
    p = p0 * e ** ((-1) * (h / H))
    ro = p * 1.2230948554874
    Fd = 1 / 2 * ro * d * A * ((Vy / cos_f) ** 2)
    Fd = 0
    dVy = (((F * cos_f) / (m0 - k * tl)) - GM / (r + h) ** 2 - Fd * cos_f / (m0 - k * tl)) * dt
    vs.append(Vy)
    Vy = Vy + dVy
    dh = Vy * dt

    jj+=1
    if tg > 140:
        break
    hg.append(h)
    h = h + dh

plt.title("Взлёт" + '\n' + "Зависимость массы от времени")
plt.xlabel("Время, с")
plt.ylabel("Масса, кг")
plt.plot(ti, ms, color="red", label='Мат Модель')
plt.plot(dataT, dataM, label='KSP')
plt.legend()
plt.grid(True)
plt.show()