import json

# загружаем
data = json.load(open('C:\\Users\\supra\\Music\\prod\\prog\\dataset\\encoded.json', encoding='utf-8'))
vocab = json.load(open('C:\\Users\\supra\\Music\\prod\\prog\\dataset\\vocab.json', encoding='utf-8'))
inv_vocab = {v: k for k, v in vocab.items()}

# порог
LIMIT = 128

# фильтруем
clean = [seq for seq in data if len(seq) <= LIMIT]
removed = len(data) - len(clean)

# сохраняем
with open('C:\\Users\\supra\\Music\\prod\\prog\\dataset\\encoded_clean.json', 'w', encoding='utf-8') as f:
    json.dump(clean, f, ensure_ascii=False)

# сохраняем человекочитаемо
with open('C:\\Users\\supra\\Music\\prod\\prog\\dataset\\datasetA_clean.txt', 'w', encoding='utf-8') as f:
    for seq in clean:
        text = "".join(inv_vocab[i] for i in seq if i not in (0, 2, 3))
        f.write(text + "\n")

# статистика
lengths = [len(x) for x in clean]
print(f"Удалено реплик: {removed}")
print(f"Осталось: {len(clean)}")
print(f"Токенов всего: {sum(lengths)}")
print(f"Минимум: {min(lengths)}")
print(f"Максимум: {max(lengths)}")
print(f"Медиана: {sorted(lengths)[len(lengths)//2]}")
print(f"Среднее: {sum(lengths)/len(lengths):.1f}")

# проверка
assert max(lengths) <= LIMIT, "Ошибка: есть реплики длиннее порога!"
print("✅ Максимум ≤ 128 — ок")