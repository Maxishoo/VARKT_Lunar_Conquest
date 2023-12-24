import math
L = 11_400_000
v0 = 939
g = 1

inner = (L * g) / (v0 ** 2)
print(inner / (1 + abs(inner)))
angle = 1/2 * math.asin(inner / (1 + abs(inner)))

print(angle)
