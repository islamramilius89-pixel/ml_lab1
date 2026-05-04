# train.py - скрипт для обучения модели определения вида пингвина

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
import configparser

print("=" * 50)
print("НАЧАЛО ОБУЧЕНИЯ МОДЕЛИ")
print("=" * 50)

# --------------------------------------------------
# ШАГ 1: Загрузка параметров из config.ini
# --------------------------------------------------
print("\n[1] Загружаем параметры модели из config.ini...")

config = configparser.ConfigParser()
config.read("config.ini")

n_estimators = config.getint("MODEL", "n_estimators")
max_depth = config.getint("MODEL", "max_depth")
random_state = config.getint("MODEL", "random_state")

print(f"    → Количество деревьев (n_estimators): {n_estimators}")
print(f"    → Максимальная глубина (max_depth): {max_depth}")
print(f"    → Случайное зерно (random_state): {random_state}")

# --------------------------------------------------
# ШАГ 2: Загрузка данных
# --------------------------------------------------
print("\n[2] Загружаем данные из файла data/penguins_size.csv...")

df = pd.read_csv("data/penguins_size.csv")
print(f"    → Загружено строк: {len(df)}")
print(f"    → Колонки: {list(df.columns)}")

# --------------------------------------------------
# ШАГ 3: Очистка данных (удаляем строки с пропусками)
# --------------------------------------------------
print("\n[3] Очищаем данные - удаляем строки с пропущенными значениями...")

rows_before = len(df)
df = df.dropna()
rows_after = len(df)
removed = rows_before - rows_after
print(f"    → Было строк: {rows_before}")
print(f"    → Стало строк: {rows_after}")
print(f"    → Удалено строк: {removed}")

# --------------------------------------------------
# ШАГ 4: Выбор признаков и целевой переменной
# --------------------------------------------------
print("\n[4] Выбираем признаки для обучения...")

# Признаки (на основе которых будем предсказывать)
feature_columns = ["culmen_length_mm", "culmen_depth_mm", "flipper_length_mm", "body_mass_g"]
X = df[feature_columns]

# Целевая переменная (что предсказываем)
y = df["species"]

print(f"    → Признаки (X): {feature_columns}")
print(f"    → Цель (y): species")
print(f"    → Размер X: {X.shape}")
print(f"    → Размер y: {y.shape}")

# --------------------------------------------------
# ШАГ 5: Создание и обучение модели
# --------------------------------------------------
print("\n[5] Создаём и обучаем модель RandomForestClassifier...")

model = RandomForestClassifier(
    n_estimators=n_estimators,
    max_depth=max_depth,
    random_state=random_state
)

print(f"    → Модель создана. Начинаем обучение...")

model.fit(X, y)

print(f"    → Обучение завершено!")

# --------------------------------------------------
# ШАГ 6: Сохранение модели в файл
# --------------------------------------------------
print("\n[6] Сохраняем обученную модель в файл model.pkl...")

joblib.dump(model, "model.pkl")

print(f"    → Модель сохранена в файл: model.pkl")
print(f"    → Размер файла: ", end="")

import os
size = os.path.getsize("model.pkl")
if size < 1024:
    print(f"{size} байт")
elif size < 1024*1024:
    print(f"{size / 1024:.1f} КБ")
else:
    print(f"{size / (1024*1024):.1f} МБ")

# --------------------------------------------------
# ШАГ 7: Проверка модели на примере
# --------------------------------------------------
print("\n[7] Проверяем модель на одном примере...")

# Берём первого пингвина из данных
first_penguin = X.iloc[0:1]
true_species = y.iloc[0]
predicted_species = model.predict(first_penguin)[0]

print(f"    → Пример пингвина: {dict(zip(feature_columns, first_penguin.values[0]))}")
print(f"    → Истинный вид: {true_species}")
print(f"    → Предсказанный вид: {predicted_species}")

if true_species == predicted_species:
    print(f"    → ✅ Предсказание верное!")
else:
    print(f"    → ❌ Предсказание неверное!")

# --------------------------------------------------
# ИТОГИ
# --------------------------------------------------
print("\n" + "=" * 50)
print("ОБУЧЕНИЕ ЗАВЕРШЕНО УСПЕШНО!")
print("=" * 50)
print("\nСозданные файлы:")
print("  - model.pkl  (обученная модель)")
print("\nТеперь можно запустить API командой:")
print("  python -m uvicorn main:app --reload")