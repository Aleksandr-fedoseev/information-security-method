import numpy as np
import matplotlib.pyplot as plt

# 1. Параметры времени и разбиения (из методички)
T_block = 2.0         # Длительность одного кадра T (2 секунды)
n_blocks = 3          # Количество кадров (всего 6 секунд)
n_segments = 5        # На сколько кусочков режем каждый кадр (n = 5)
total_time = n_blocks * T_block
n_samples = 1500      # Всего точек во времени (по 100 точек на каждый кусочек)

# Временная шкала от 0 до 6 секунд, по сути 1500 точек на отрезке от 0 до 6
t = np.linspace(0, total_time, n_samples)

# 2. Генерация исходного сигнала X(t) по формуле из методички
A, B, C = 2.0, 1.5, 0.5
alpha, beta, gamma = 6.0, 18.0, 4.0
X = A * np.sin(alpha * t) + B * np.cos(beta * t) + t * C * np.cos(np.cos(gamma * t))

# 3. Ключ скремблирования 
key = [3, 0, 4, 1, 2]

# Обратный ключ для расшифровки (куда вернуть каждый кусочек)
inv_key = [key.index(i) for i in range(len(key))]

# 4. Скремблирование (шифрование звука)
scrambled_blocks = []
for block in np.split(X, n_blocks): # Режем массив из точек на три части
    segments = np.split(block, n_segments)                             # разрезали кадр на 5 кусочков
    scrambled_blocks.append(np.concatenate([segments[i] for i in key])) # перемешали их по ключу

Y = np.concatenate(scrambled_blocks)                                  # соединили кадры в единый сигнал

# 5. Дескремблирование (расшифровка на приемнике)
descrambled_blocks = []
for block in np.split(Y, n_blocks):
    segments = np.split(block, n_segments)                                 # разрезали зашифрованный кадр
    descrambled_blocks.append(np.concatenate([segments[i] for i in inv_key])) # расставили кусочки на свои места

X_rec = np.concatenate(descrambled_blocks)

# 6. Проверка точности восстановления
max_error = np.max(np.abs(X - X_rec))
print("=" * 60)
print("РЕЗУЛЬТАТЫ СКРЕМБЛИРОВАНИЯ:")
print(f"Ключ шифрования (прямой):    {key}")
print(f"Ключ расшифровки (обратный): {inv_key}")
print(f"Максимальная ошибка:         {max_error:.2e} (восстановлен идеально!)")
print("=" * 60)

# 7. Построение 3 графиков
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 7), sharex=True)

ax1.plot(t, X, color="blue", linewidth=1.5)
ax1.set_title("1. Исходный аналоговый сигнал X(t)", fontsize=11, fontweight="bold")
ax1.set_ylabel("Амплитуда")
ax1.grid(True, linestyle=":", alpha=0.6)

ax2.plot(t, Y, color="crimson", linewidth=1.5)
ax2.set_title(f"2. Зашифрованный сигнал в канале связи Y(t) (ключ {key})", fontsize=11, fontweight="bold")
ax2.set_ylabel("Амплитуда")
ax2.grid(True, linestyle=":", alpha=0.6)

ax3.plot(t, X_rec, color="green", linewidth=1.5)
ax3.set_title("3. Восстановленный сигнал на приемнике X_rec(t)", fontsize=11, fontweight="bold")
ax3.set_xlabel("Время t (секунды)")
ax3.set_ylabel("Амплитуда")
ax3.grid(True, linestyle=":", alpha=0.6)

plt.tight_layout()
plt.show()
