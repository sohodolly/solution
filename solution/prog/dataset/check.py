import json

data = json.load(open('C:\\Users\\supra\\Music\\prod\\prog\\dataset\\encoded.json', encoding='utf-8'))
lengths = sorted(len(x) for x in data)

print(f"Всего реплик: {len(lengths)}")
print(f"Минимум: {lengths[0]}")
print(f"Максимум: {lengths[-1]}")
print(f"Медиана: {lengths[len(lengths)//2]}")
print(f"Среднее: {sum(lengths)/len(lengths):.1f}")

print("\nРаспределение по длинам:")
for limit in [16, 32, 48, 64, 96, 128, 256]:
    count = sum(1 for l in lengths if l > limit)
    print(f"  > {limit}: {count} реплик")