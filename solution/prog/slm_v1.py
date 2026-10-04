import json
import re
import sys
from pathlib import Path


class ChatApp:
    def __init__(self):
        self.chats = []

    # ---------- ТОКЕНИЗАЦИЯ ----------
    def _normalize_text(self, value):
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
                    t = item.get('text')
                    if isinstance(t, str):
                        parts.append(t)
            return "".join(parts)
        if isinstance(value, dict):
            t = value.get('text')
            if isinstance(t, str):
                return t
        return str(value)

    def write_dataset(self, json_path):
        print(f"[write_dataset] вызван с путём: {json_path}")
        chat_data = self.load_chat_data(Path(json_path))
        if not chat_data:
            print("Не удалось загрузить данные чата.")
            return

        dataset_dir = Path(__file__).parent / "dataset"
        dataset_dir.mkdir(exist_ok=True)
        dataset_path = dataset_dir / "datasetA.txt"
        vocab_path = dataset_dir / "vocab.json"
        encoded_path = dataset_dir / "encoded.json"

        messages = []
        if isinstance(chat_data, list):
            messages = chat_data
        elif isinstance(chat_data, dict) and 'messages' in chat_data:
            messages = chat_data['messages']

        if not messages:
            print("Нет сообщений для токенизации.")
            return

        # 1. Собираем ЦЕЛЫЕ реплики (не разбиваем на слова)
        lines = []
        for msg in messages:
            if not isinstance(msg, dict):
                continue
            text = self._normalize_text(msg.get('text'))
            # убираем переводы строк внутри реплики, чтобы одна реплика = одна строка
            text = text.replace('\n', ' ').strip()
            if text:
                lines.append(text)

        if not lines:
            print("Не удалось получить ни одной реплики.")
            return

        # 2. Собираем ВСЕ символы, которые встречаются в датасете
        #    + спецтокены для начала/конца/неизвестного/паддинга
        all_text = "\n".join(lines)
        chars = sorted(set(all_text))

        # спецтокены идут первыми
        vocab = {
            "<PAD>": 0,
            "<UNK>": 1,
            "<BOS>": 2,
            "<EOS>": 3,
        }
        for i, ch in enumerate(chars, start=len(vocab)):
            vocab[ch] = i

        inv_vocab = {v: k for k, v in vocab.items()}

        # 3. Кодируем каждую реплику в массив чисел
        #    в начало и конец добавляем <BOS> и <EOS>
        encoded = []
        for line in lines:
            ids = [vocab["<BOS>"]]
            for ch in line:
                ids.append(vocab.get(ch, vocab["<UNK>"]))
            ids.append(vocab["<EOS>"])
            encoded.append(ids)

        # 4. Сохраняем всё на диск
        # человекочитаемый датасет — по одной реплике на строку
        with open(dataset_path, "w", encoding="utf-8") as f:
            for line in lines:
                f.write(line + "\n")

        # словарь
        with open(vocab_path, "w", encoding="utf-8") as f:
            json.dump(vocab, f, ensure_ascii=False, indent=2)

        # закодированные реплики (числа)
        with open(encoded_path, "w", encoding="utf-8") as f:
            json.dump(encoded, f, ensure_ascii=False)

        # отчёт
        total_tokens = sum(len(ids) for ids in encoded)
        print(f"\n✅ Датасет готов:")
        print(f"   datasetA.txt  — {len(lines)} реплик (человекочитаемо)")
        print(f"   vocab.json    — {len(vocab)} уникальных токенов")
        print(f"   encoded.json  — {total_tokens} токенов всего (числа)")
        print(f"\n   Размер словаря: {len(vocab)}")
        print(f"   Пример первой реплики: {lines[0][:80]}")
        print(f"   Её токены: {encoded[0][:20]}...")

    # ---------- СОЦСЕТЬ ----------
    def ask_social_network(self):
        print("\nВыберите соцсеть:")
        print("1. Telegram")
        print("2. WhatsApp")
        while True:
            choice = input("Ваш выбор (1/2): ").strip()
            if choice == '1':
                return 'telegram'
            elif choice == '2':
                return 'whatsapp'
            else:
                print("Введите 1 или 2.")

    # ---------- ЧАТЫ ----------
    def show_chats(self):
        while True:
            print("\n" + "=" * 50)
            print("МОИ ЧАТЫ")
            print("=" * 50)

            if self.chats:
                for idx, chat in enumerate(self.chats, 1):
                    print(f"{idx}. Чат с {chat.get('other_person', '?')} ({chat.get('social_network', '?')})")
                print(f"{len(self.chats) + 1}. Добавить чат из файла")
                print("[0] Вернуться в главное меню")

                choice = input("\nВыберите номер чата или действие: ").strip()

                if choice == '0':
                    break
                elif choice == str(len(self.chats) + 1):
                    self.add_chat_from_file()
                elif choice.isdigit() and 1 <= int(choice) <= len(self.chats):
                    chat = self.chats[int(choice) - 1]
                    self.show_chat_content(chat['file_path'], chat['social_network'])
                else:
                    print("Неверный выбор. Попробуйте ещё раз.")
            else:
                print("У вас пока нет чатов.")
                print("1. Добавить чат из файла")
                print("0. Вернуться в главное меню")

                choice = input("\nВаш выбор: ").strip()
                if choice == '1':
                    self.add_chat_from_file()
                elif choice == '0':
                    break
                else:
                    print("Неверный выбор.")

    def add_chat_from_file(self):
        print("\n" + "=" * 50)
        print("ДОБАВЛЕНИЕ ЧАТА ИЗ ФАЙЛА")
        print("=" * 50)

        file_path = input("Введите путь к JSON-файлу с перепиской: ").strip()
        if not file_path:
            print("Путь не указан.")
            return
        json_path = Path(file_path)
        if not json_path.exists():
            print(f"Файл {json_path} не найден.")
            return
        if json_path.is_dir():
            json_path = json_path / "result.json"
            if not json_path.exists():
                print(f"Файл {json_path} не найден.")
                return

        social_network = self.ask_social_network()
        self.write_dataset(json_path)
        other = self.analyze_chat_and_get_other_person(json_path)
        if other:
            chat_info = {
                'social_network': social_network,
                'other_person': other,
                'file_path': str(json_path)
            }
            self.chats.append(chat_info)
            print(f"\nЧат с '{other}' успешно добавлен!")
        else:
            print("\nНе удалось определить второго участника переписки.")

        input("\nНажмите Enter для продолжения...")

    def show_chat_content(self, json_path, social_network):
        print(f"\nОткрываю чат из {social_network}...")
        chat_data = self.load_chat_data(Path(json_path))

        if chat_data:
            sender_names = self.extract_sender_names(chat_data)
            if sender_names:
                print(f"\nУчастники переписки: {', '.join(sorted(sender_names))}")
                if len(sender_names) == 2:
                    print(f"(В переписке участвуют двое: {', '.join(sorted(sender_names))})")
                else:
                    print(f"(Всего уникальных отправителей: {len(sender_names)})")
            if isinstance(chat_data, list) and len(chat_data) > 0:
                print("\nПоследние сообщения (макс. 5):")
                for msg in chat_data[-5:]:
                    sender = msg.get('sender_name', 'Неизвестный')
                    text = self._normalize_text(msg.get('text'))[:60]
                    print(f"  {sender}: {text}...")
        else:
            print("Не удалось загрузить данные чата.")

        input("\nНажмите Enter для продолжения...")

    # ---------- ВСПОМОГАТЕЛЬНЫЕ ----------
    def load_chat_data(self, json_path):
        json_path = Path(json_path)
        if json_path.is_dir():
            print(f"{json_path} — это папка, а не файл.")
            return None
        try:
            with open(json_path, encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Файл {json_path} не найден.")
            return None
        except PermissionError:
            print(f"Нет доступа к файлу {json_path}.")
            return None
        except json.JSONDecodeError:
            print(f"Файл {json_path} содержит некорректный JSON.")
            return None
        except OSError as e:
            print(f"Ошибка чтения файла {json_path}: {e}")
            return None

    def extract_sender_names(self, chat_data):
        names = set()

        if isinstance(chat_data, list):
            for msg in chat_data:
                if not isinstance(msg, dict):
                    continue
                name = msg.get('sender_name')
                if name and isinstance(name, str):
                    names.add(name.strip())
        elif isinstance(chat_data, dict):
            if 'messages' in chat_data:
                for msg in chat_data['messages']:
                    if not isinstance(msg, dict):
                        continue
                    sender = msg.get('from') or msg.get('sender') or msg.get('actor')
                    if sender and isinstance(sender, str):
                        names.add(sender.strip())
            else:
                if 'members' in chat_data:
                    for member in chat_data['members']:
                        if not isinstance(member, dict):
                            continue
                        name = member.get('name')
                        if name and isinstance(name, str):
                            names.add(name.strip())
                if 'participants' in chat_data:
                    for p in chat_data['participants']:
                        if not isinstance(p, dict):
                            continue
                        name = p.get('name')
                        if name and isinstance(name, str):
                            names.add(name.strip())
        return names

    def analyze_chat_and_get_other_person(self, json_path):
        print("\nАнализирую переписку...")

        chat_data = self.load_chat_data(json_path)
        if not chat_data:
            return None

        sender_names = self.extract_sender_names(chat_data)

        if not sender_names:
            print("Не удалось извлечь имена участников из JSON.")
            return None

        names_list = sorted(sender_names)
        print(f"Найденные участники: {', '.join(names_list)}")

        if len(names_list) < 2:
            print("В переписке меньше двух участников.")
            return None

        print("\nКто из них — вы?")
        for idx, name in enumerate(names_list, 1):
            print(f"{idx}. {name}")
        while True:
            choice = input("Ваш выбор (номер): ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(names_list):
                my_name = names_list[int(choice) - 1]
                break
            else:
                print("Неверный выбор.")

        other_names = [n for n in names_list if n != my_name]

        if len(other_names) == 1:
            other_person = other_names[0]
            print(f"Ваш собеседник: {other_person}")
            return other_person
        else:
            print("\nВ переписке несколько собеседников. Выберите нужного:")
            for idx, name in enumerate(other_names, 1):
                print(f"{idx}. {name}")
            while True:
                choice = input("Ваш выбор (номер): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(other_names):
                    return other_names[int(choice) - 1]
                else:
                    print("Неверный выбор.")

    # ---------- ГЛАВНОЕ МЕНЮ ----------
    def main_menu(self):
        while True:
            print("\n" + "=" * 50)
            print("ГЛАВНОЕ МЕНЮ")
            print("=" * 50)
            print("1. Мои чаты")
            print("0. Выход")
            print("=" * 50)

            choice = input("Выберите действие: ").strip()

            if choice == '1':
                self.show_chats()
            elif choice == '0':
                print("\nДо свидания!")
                sys.exit(0)
            else:
                print("Неверный выбор. Попробуйте ещё раз.")

    def run(self):
        print("=" * 50)
        print("ЧАТ-МЕНЕДЖЕР")
        print("=" * 50)
        self.main_menu()


if __name__ == "__main__":
    app = ChatApp()
    app.run()
