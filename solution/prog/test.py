import json
data = json.load(open('C:\\Users\\supra\\Music\\prod\\prog\\dataset\\encoded.json', encoding='utf-8'))
total = sum(len(x) for x in data)
print(f"Реплик: {len(data)}")
print(f"Токенов всего: {total}")
print(f"Средняя длина: {total / len(data):.1f}")