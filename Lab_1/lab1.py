import math
import matplotlib.pyplot as plt

# 1. Исходные данные
y_fence , x_fence_max = 45.0, 50.0  # Координаты забора (длина 50 м, Y = 45)
k1, k2 = 2.0, 0.5                  # Защищенность: k1, k2
y_win = 25.0                       # Стена с окнами (Y = 25)
x_win1, p_win1 = 15.0, 0.7         # Окно 1: X = 15, 
x_win2, p_win2 = 35.0, 0.4         # Окно 2: X = 35,
x_inf, y_inf = 20.0, 10.0          # Сейф с информацией (X = 20, Y = 10)
n = 100                            # Количество точек на заборе

# 2. Расстояния внутри здания
l1_2 = math.sqrt((x_win1 - x_inf)**2 + (y_win - y_inf)**2)  # Окно 1 -> сейф
l2_2 = math.sqrt((x_win2 - x_inf)**2 + (y_win - y_inf)**2)  # Окно 2 -> сейф

# Списки для построения графиков
x_list = []
p1_list = []
p2_list = []

# Переменные для поиска минимума и максимума
min_val = float('inf')  # самый защищенный маршрут
max_val = -1.0          # самый уязвимый маршрут
min_route = None        # сохраним
max_route = None

# 3. Основной цикл: перебираем 100 точек на заборе
step = x_fence_max / (n - 1)  # шаг между точками на заборе

for i in range(n):
    x = i * step # Где сейчас стоит нарушитель
    
    # 1. Расстояния по двору: от точки забора (x, y_fence) до окон
    l1_1 = math.sqrt((x - x_win1)**2 + (y_fence - y_win)**2)
    l2_1 = math.sqrt((x - x_win2)**2 + (y_fence - y_win)**2)
    
    # 2. P = (k1 / l1) * P_окна * (k2 / l2)
    p1 = (k1 / l1_1) * p_win1 * (k2 / l1_2)  # через Окно 1
    p2 = (k1 / l2_1) * p_win2 * (k2 / l2_2)  # через Окно 2
    
    x_list.append(x)
    p1_list.append(p1)
    p2_list.append(p2)
    
    # 3. Ищем минимум и максимум 
    for p, win_num in [(p1, 1), (p2, 2)]:
        if p < min_val:
            min_val = p
            min_route = (x, win_num)
        if p > max_val:
            max_val = p
            max_route = (x, win_num)

# 4. Вывод результатов
print("=" * 60)
print("РЕЗУЛЬТАТЫ РАСЧЕТА:")
print(f"1. Минимум (наиболее защищенный маршрут):")
print(f"   Вероятность P = {min_val:.6f}")
print(f"   Точка на заборе X = {min_route[0]:.2f} м, через Окно №{min_route[1]}")
print(f"\n2. Максимум (наиболее уязвимый маршрут):")
print(f"   Вероятность P = {max_val:.6f}")
print(f"   Точка на заборе X = {max_route[0]:.2f} м, через Окно №{max_route[1]}")
print("=" * 60)

# 5. Построение графика
plt.figure(figsize=(9, 5))
plt.plot(x_list, p1_list, label="Через Окно 1 (P_i1)", color="orange", linewidth=2)
plt.plot(x_list, p2_list, label="Через Окно 2 (P_i2)", color="blue", linewidth=2)

# Отмечаем точки минимума и максимума
plt.scatter([min_route[0]], [min_val], color="green", s=90, zorder=5, 
            label=f"Минимум ({min_val:.5f}) в X={min_route[0]:.1f}")
plt.scatter([max_route[0]], [max_val], color="red", s=90, zorder=5, 
            label=f"Максимум ({max_val:.5f}) в X={max_route[0]:.1f}")

plt.title("Распределение вероятностей проникновения вдоль забора", fontsize=12)
plt.xlabel("Координата точки на заборе X (метры)", fontsize=10)
plt.ylabel("Вероятность проникновения P", fontsize=10)
plt.legend()
plt.grid(True, linestyle=":", alpha=0.6)
plt.tight_layout()
plt.show()
