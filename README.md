# 🛸 UFO Sightings — LLM Analysis Pipeline

> Автоматический пайплайн для анализа наблюдений НЛО с помощью искусственного интеллекта

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Groq](https://img.shields.io/badge/LLM-Groq%20API-orange)
![Model](https://img.shields.io/badge/Model-LLaMA%203.3%2070B-green)
![Records](https://img.shields.io/badge/Обработано-30%20записей-purple)

---

## 📌 О проекте

Скрипт читает текстовые описания очевидцев НЛО из датасета **NUFORC** (80 332 записей),
отправляет каждое описание в языковую модель через **Groq API** и получает
структурированный **JSON-ответ** с извлечёнными характеристиками наблюдения.

### Что делает пайплайн
📄 ufo_sightings.csv
↓
🔍 Фильтрация и подготовка данных
↓
🤖 Запрос к LLM (llama-3.3-70b-versatile)
↓
📦 Парсинг JSON-ответа
↓
💾 results.json
---

## 🧠 Что извлекает модель

Для каждого наблюдения LLM возвращает структурированный JSON:

| Поле | Описание | Пример |
|------|----------|--------|
| `witness_emotion` | Эмоция очевидца | `excitement` |
| `object_color` | Цвет объекта | `orange` |
| `object_behavior` | Поведение объекта | `hovering` |
| `duration_plausible` | Правдоподобна ли длительность | `true` |
| `credibility` | Достоверность описания | `medium` |
| `summary_ru` | Краткое резюме на русском | `Очевидец наблюдал...` |

---

## 📁 Структура репозитория
ufo-llm-pipeline/
├── 📜 pipeline.py          # основной скрипт пайплайна
├── 📊 ufo_sightings.csv    # входной датасет (NUFORC)
├── 📦 results.json         # результат работы скрипта
└── 📖 README.md
---

## ⚙️ Установка и запуск

### 1. Установи зависимости

```bash
pip install groq pandas
```

### 2. Вставь свой Groq API ключ в `pipeline.py`

```python
API_KEY = "your_groq_api_key_here"
```

Получить бесплатный ключ: [console.groq.com](https://console.groq.com)

### 3. Запусти скрипт

```bash
python pipeline.py
```

### 4. Результат

Скрипт выведет прогресс в терминал и сохранит `results.json`:
Загружаем датасет...
Отобрано записей: 30
Запускаем пайплайн...
[01/30] 10/10/1949 | cylinder   | us → ✓ low    | confusion
[02/30] 10/10/1955 | circle     | gb → ✓ medium | excitement
...
[30/30] 10/10/1980 | sphere     | us → ✓ medium | excitement
══════════════════════════════════════
Готово! Обработано: 30/30, ошибок: 0
Результат сохранён: results.json
══════════════════════════════════════
---

## 📊 Результаты анализа

### Достоверность описаний

| Уровень | Количество | Доля |
|---------|------------|------|
| 🔴 low | 16 | 53% |
| 🟡 medium | 13 | 43% |
| 🟢 high | 1 | 4% |

### Эмоции очевидцев

| Эмоция | Количество |
|--------|------------|
| 😲 excitement | 14 |
| 😕 confusion | 8 |
| 😱 shock | 4 |
| 😨 fear | 2 |
| 😐 calm | 2 |

---

## 📥 Пример входных данных

```csv
date_time,city_area,country,ufo_shape,description
10/10/1949 20:30,san marcos,us,cylinder,"This event took place in early fall around 1949..."
10/10/1955 17:00,chester,gb,circle,"Green/Orange circular disc over Chester, England"
```

## 📤 Пример выходных данных

```json
{
  "meta": {
    "dataset": "UFO Sightings NUFORC",
    "model": "llama-3.3-70b-versatile",
    "total_processed": 30,
    "total_errors": 0
  },
  "results": [
    {
      "id": 1,
      "shape": "cylinder",
      "country": "us",
      "date": "10/10/1949 20:30",
      "witness_emotion": "confusion",
      "object_color": "unknown",
      "object_behavior": "hovering",
      "duration_plausible": true,
      "credibility": "low",
      "summary_ru": "Очевидец наблюдал цилиндрический объект в 1949 году после встречи бойскаутов в церкви."
    }
  ]
}
```

---

## 🗃️ Источник данных

Датасет: **UFO Sightings — NUFORC** (National UFO Reporting Center)
- 80 332 наблюдения с 1906 по 2014 год
- Источник: [TidyTuesday 2019-06-25](https://github.com/rfordatascience/tidytuesday/tree/main/data/2019/2019-06-25)
