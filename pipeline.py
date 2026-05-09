import pandas as pd
import json
import time
from groq import Groq

# ── настройки ──────────────────────────────────────────────
API_KEY   = "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"
CSV_PATH  = "ufo_sightings.csv"
OUT_PATH  = "results.json"
MODEL     = "llama-3.3-70b-versatile"
N_RECORDS = 30  # сколько записей обрабатываем

client = Groq(api_key=API_KEY)

# ── загрузка данных ────────────────────────────────────────
print("Загружаем датасет...")
df = pd.read_csv(CSV_PATH, encoding="utf-8", on_bad_lines="skip")

# Берём записи где есть описание и форма
df_clean = df.dropna(subset=["description", "ufo_shape", "country"]).head(N_RECORDS).copy()
df_clean = df_clean.reset_index(drop=True)

print(f"Отобрано записей: {len(df_clean)}")

# ── функция запроса к LLM ──────────────────────────────────
def analyze_sighting(row_id, description, shape, country, date):
    prompt = f"""Ты — аналитик данных. Проанализируй описание наблюдения НЛО и верни ТОЛЬКО валидный JSON без каких-либо пояснений, markdown-разметки и блоков кода.

Описание наблюдения:
\"\"\"{description[:600]}\"\"\"

Метаданные: форма объекта — {shape}, страна — {country}, дата — {date}

Верни JSON строго в таком формате:
{{
  "id": {row_id},
  "shape": "{shape}",
  "country": "{country}",
  "date": "{date}",
  "witness_emotion": "одно слово на английском — эмоция очевидца (fear/excitement/confusion/calm/shock)",
  "object_color": "цвет объекта из описания или unknown",
  "object_behavior": "одно-два слова — поведение объекта (hovering/moving fast/rotating/blinking/silent)",
  "duration_plausible": true или false — правдоподобна ли длительность наблюдения,
  "credibility": "low/medium/high — насколько описание выглядит достоверным",
  "summary_ru": "1-2 предложения на русском — краткое содержание наблюдения"
}}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()

# ── основной пайплайн ──────────────────────────────────────
results = []
errors  = []

print("\nЗапускаем пайплайн...\n")

for i, row in df_clean.iterrows():
    record_id = i + 1
    desc    = str(row.get("description", ""))
    shape   = str(row.get("ufo_shape", "unknown"))
    country = str(row.get("country", "unknown"))
    date    = str(row.get("date_time", "unknown"))

    print(f"[{record_id:02d}/{N_RECORDS}] {date[:10]} | {shape:10} | {country} ", end="")

    try:
        raw = analyze_sighting(record_id, desc, shape, country, date)

        # Чистим ответ на случай если модель добавила лишнее
        raw_clean = raw.strip()
        if raw_clean.startswith("```"):
            raw_clean = raw_clean.split("```")[1]
            if raw_clean.startswith("json"):
                raw_clean = raw_clean[4:]
        raw_clean = raw_clean.strip()

        parsed = json.loads(raw_clean)
        results.append(parsed)
        print(f"→ ✓ {parsed.get('credibility','?')} credibility | {parsed.get('witness_emotion','?')}")

    except json.JSONDecodeError as e:
        print(f"→ ✗ Ошибка парсинга JSON: {e}")
        errors.append({"id": record_id, "error": str(e), "raw": raw})

    except Exception as e:
        print(f"→ ✗ Ошибка: {e}")
        errors.append({"id": record_id, "error": str(e)})

    time.sleep(0.5)  # пауза чтобы не превысить лимит

# ── сохранение результатов ─────────────────────────────────
output = {
    "meta": {
        "dataset": "UFO Sightings — NUFORC",
        "model": MODEL,
        "total_processed": len(results),
        "total_errors": len(errors),
        "task": "Структурированное извлечение данных из текстовых описаний наблюдений НЛО"
    },
    "results": results,
    "errors": errors
}

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

# ── итоговая статистика ────────────────────────────────────
print(f"\n{'═'*50}")
print(f"  Готово!")
print(f"  Успешно обработано : {len(results)} из {N_RECORDS}")
print(f"  Ошибок             : {len(errors)}")
print(f"  Результат сохранён : {OUT_PATH}")

if results:
    emotions   = [r.get("witness_emotion","?") for r in results]
    credibility = [r.get("credibility","?") for r in results]
    print(f"\n  Распределение достоверности:")
    for level in ["high","medium","low"]:
        count = credibility.count(level)
        bar   = "█" * count
        print(f"    {level:6} : {bar} {count}")
    print(f"\n  Топ эмоций очевидцев:")
    from collections import Counter
    for emotion, count in Counter(emotions).most_common(5):
        print(f"    {emotion:12}: {count}")
print(f"{'═'*50}\n")