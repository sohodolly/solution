import json
import re
from pathlib import Path

RAW_PATH = Path("C:\\Users\\supra\\Music\\prod\\prog\\result.json")
OUT_DIR = Path("C:\\Users\\supra\\Music\\prod\\prog\\dataset")
OUT_DIR.mkdir(exist_ok=True)

ME = "supra"
OTHER = "murunen🩷"

LIMIT = 128  # максимальная длина реплики в токенах (с BOS/EOS)

# ---------- 1. Загрузка ----------
with open(RAW_PATH, encoding="utf-8") as f:
    raw = json.load(f)

messages = raw["messages"] if isinstance(raw, dict) else raw
print(f"Всего записей: {len(messages)}")

# ---------- 2. Нормализация текста ----------
def normalize_text(value):
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                t = item.get("text")
                if isinstance(t, str):
                    parts.append(t)
        return "".join(parts)
    if isinstance(value, dict):
        t = value.get("text")
        if isinstance(t, str):
            return t
    return str(value)

# ---------- 3. Сбор реплик с маркерами ----------
lines = []
for msg in messages:
    if not isinstance(msg, dict):
        continue
    if msg.get("type") != "message":
        continue  # пропускаем service

    sender = msg.get("from")
    text = normalize_text(msg.get("text"))
    text = text.replace("\n", " ").strip()
    if not text:
        continue

    if sender == ME:
        lines.append(f"<Я> {text}")
    elif sender == OTHER:
        lines.append(f"<ОН> {text}")
    # остальные отправители — игнорируем

print(f"Реплик после фильтрации: {len(lines)}")

# ---------- 4. Словарь ----------
all_text = "\n".join(lines)
chars = sorted(set(all_text))

vocab = {
    "<PAD>": 0,
    "<UNK>": 1,
    "<BOS>": 2,
    "<EOS>": 3,
}
for i, ch in enumerate(chars, start=len(vocab)):
    vocab[ch] = i

inv_vocab = {v: k for k, v in vocab.items()}

# ---------- 5. Кодирование с обрезкой по LIMIT ----------
encoded = []
skipped = 0
for line in lines:
    ids = [vocab["<BOS>"]]
    for ch in line:
        ids.append(vocab.get(ch, vocab["<UNK>"]))
    ids.append(vocab["<EOS>"])
    if len(ids) > LIMIT:
        skipped += 1
        continue
    encoded.append(ids)

print(f"Обрезано реплик (> {LIMIT}): {skipped}")
print(f"Осталось реплик: {len(encoded)}")

# ---------- 6. Сохранение ----------
with open(OUT_DIR / "datasetA.txt", "w", encoding="utf-8") as f:
    for line in lines:
        f.write(line + "\n")

with open(OUT_DIR / "vocab.json", "w", encoding="utf-8") as f:
    json.dump(vocab, f, ensure_ascii=False, indent=2)

with open(OUT_DIR / "encoded.json", "w", encoding="utf-8") as f:
    json.dump(encoded, f, ensure_ascii=False)

# ---------- 7. Статистика ----------
total_tokens = sum(len(x) for x in encoded)
lengths = [len(x) for x in encoded]

print("\n✅ Датасет готов:")
print(f"   datasetA.txt  — {len(lines)} реплик (все, до обрезки)")
print(f"   vocab.json    — {len(vocab)} токенов")
print(f"   encoded.json  — {len(encoded)} реплик, {total_tokens} токенов")
print(f"\n   Средняя длина: {total_tokens/len(encoded):.1f}")
print(f"   Минимум: {min(lengths)}")
print(f"   Максимум: {max(lengths)}")
print(f"   Медиана: {sorted(lengths)[len(lengths)//2]}")
print(f"   Размер словаря: {len(vocab)}")