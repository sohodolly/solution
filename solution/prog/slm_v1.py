import json
import os
from pathlib import Path
import sys

# ========== ДОПОЛНИТЕЛЬНЫЙ КОД С МЕНЮ И УПРАВЛЕНИЕМ ==========

class UserProfile:
    def __init__(self, username):
        self.username = username
        self.has_subscription = False
        self.social_networks = {}  # {social_network: user_nickname}
        self.chats = []  # список чатов: [{'social_network': 'telegram', 'other_person': 'бодя', 'file_path': 'result.json'}]

class ChatApp:
    def __init__(self):
        self.current_user = None
        self.load_user_data()
    
    def load_user_data(self):
        """Загружает данные пользователя из файла"""
        user_data_file = Path("user_data.json")
        if user_data_file.exists():
            try:
                with open(user_data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_user = UserProfile(data['username'])
                    self.current_user.has_subscription = data.get('has_subscription', False)
                    self.current_user.social_networks = data.get('social_networks', {})
                    self.current_user.chats = data.get('chats', [])
            except:
                self.current_user = None
    
    def save_user_data(self):
        """Сохраняет данные пользователя в файл"""
        if self.current_user:
            data = {
                'username': self.current_user.username,
                'has_subscription': self.current_user.has_subscription,
                'social_networks': self.current_user.social_networks,
                'chats': self.current_user.chats
            }
            with open('user_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def show_profile(self):
        """Показывает профиль пользователя"""
        while True:
            print("\n" + "="*50)
            print(f"👤 ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ: {self.current_user.username}")
            print(f"📱 Подписка: {'Активна ✅' if self.current_user.has_subscription else 'Отсутствует ❌'}")
            print("="*50)
            
            if not self.current_user.has_subscription:
                print("\n💎 Хотите оформить подписку? (напишите '+' или 'да' для покупки)")
                answer = input("Ваш выбор: ").strip().lower()
                if answer in ['+', 'да', 'yes', 'купить', 'давай']:
                    self.current_user.has_subscription = True
                    self.save_user_data()
                    print("\n✅ Поздравляем! Подписка оформлена!")
                    print("Теперь вам доступны все функции приложения.")
                else:
                    print("\n❌ Подписка не оформлена.")
            
            print("\n[0] Вернуться в главное меню")
            choice = input("\nВведите 0 для возврата: ").strip()
            if choice == '0':
                break
    
    def show_chats(self):
        """Показывает список чатов"""
        while True:
            print("\n" + "="*50)
            print("💬 МОИ ЧАТЫ")
            print("="*50)
            
            if self.current_user.chats:
                for idx, chat in enumerate(self.current_user.chats, 1):
                    print(f"{idx}. Чат с {chat['other_person']} ({chat['social_network']})")
                print(f"{len(self.current_user.chats) + 1}. ➕ Создать новый чат")
                print("[0] Вернуться в главное меню")
                
                choice = input("\nВыберите номер чата или действие: ").strip()
                
                if choice == '0':
                    break
                elif choice == str(len(self.current_user.chats) + 1):
                    self.create_new_chat()
                elif choice.isdigit() and 1 <= int(choice) <= len(self.current_user.chats):
                    chat = self.current_user.chats[int(choice) - 1]
                    self.run_chat_analysis(chat['file_path'], chat['social_network'])
                else:
                    print("❌ Неверный выбор. Попробуйте снова.")
            else:
                print("📭 У вас пока нет чатов.")
                print("1. ➕ Создать новый чат")
                print("0. Вернуться в главное меню")
                
                choice = input("\nВаш выбор: ").strip()
                if choice == '1':
                    self.create_new_chat()
                elif choice == '0':
                    break
                else:
                    print("❌ Неверный выбор.")
    
    def create_new_chat(self):
        """Создаёт новый чат из JSON-файла"""
        print("\n" + "="*50)
        print("➕ СОЗДАНИЕ НОВОГО ЧАТА")
        print("="*50)
        
        # Спрашиваем соцсеть
        social_network = input("Из какой соцсети взята переписка? (telegram/whatsapp/viber и т.д.): ").strip().lower()
        
        # Проверяем, использовалась ли уже эта соцсеть
        if social_network in self.current_user.social_networks:
            user_nickname = self.current_user.social_networks[social_network]
            print(f"✓ Для соцсети '{social_network}' уже указан ваш никнейм: {user_nickname}")
        else:
            user_nickname = input(f"Какой у вас никнейм в {social_network}? ").strip()
            if user_nickname:
                self.current_user.social_networks[social_network] = user_nickname
                self.save_user_data()
        
        # Путь к JSON-файлу
        json_path = Path(__file__).parent / "result.json"
        if not json_path.exists():
            print(f"❌ Файл {json_path} не найден.")
            print("Пожалуйста, поместите файл 'result.json' в папку со скриптом.")
            input("Нажмите Enter для продолжения...")
            return
        
        # Запускаем анализ и получаем второго участника
        other_person = self.analyze_chat_and_get_other_person(json_path, user_nickname)
        
        if other_person:
            # Сохраняем чат
            chat_info = {
                'social_network': social_network,
                'other_person': other_person,
                'file_path': str(json_path)
            }
            self.current_user.chats.append(chat_info)
            self.save_user_data()
            print(f"\n✅ Чат с '{other_person}' успешно создан!")
        else:
            print("\n❌ Не удалось определить второго участника переписки.")
        
        input("\nНажмите Enter для продолжения...")
    
    def analyze_chat_and_get_other_person(self, json_path, user_nickname):
        """Запускает анализ чата и возвращает имя другого участника"""
        print("\n🔍 Анализирую переписку...")
        
        # Загружаем JSON
        chat_data = self.load_chat_data(json_path)
        if not chat_data:
            return None
        
        # Извлекаем имена
        sender_names = self.extract_sender_names(chat_data)
        
        if not sender_names:
            print("Не удалось извлечь имена участников из JSON.")
            return None
        
        print(f"Найдены участники: {', '.join(sorted(sender_names))}")
        
        # Проверяем, есть ли пользователь в чате
        user_found = False
        matched_user_name = None
        
        for name in sender_names:
            if name.lower() == user_nickname.lower():
                user_found = True
                matched_user_name = name
                break
        
        if not user_found:
            print(f"❌ Пользователь '{user_nickname}' НЕ найден среди участников переписки.")
            print(f"Доступные имена: {', '.join(sorted(sender_names))}")
            
            # Спрашиваем, может быть имя другое?
            answer = input("Возможно, вы используете другое имя в этой соцсети? Введите его (или Enter для отмены): ").strip()
            if answer:
                user_nickname = answer
                self.current_user.social_networks[social_network] = user_nickname
                self.save_user_data()
                
                # Проверяем снова
                for name in sender_names:
                    if name.lower() == user_nickname.lower():
                        user_found = True
                        matched_user_name = name
                        break
        
        if user_found:
            print(f"✅ Пользователь '{matched_user_name}' является участником данной переписки.")
            
            # Находим другого участника
            other_names = [name for name in sender_names if name.lower() != user_nickname.lower()]
            
            if len(other_names) == 1:
                other_person = other_names[0]
                print(f"Второй участник: {other_person}")
                return other_person
            elif len(other_names) > 1:
                print(f"В переписке несколько участников: {', '.join(other_names)}")
                print("Выберите, с кем вы хотите создать чат:")
                for idx, name in enumerate(other_names, 1):
                    print(f"{idx}. {name}")
                choice = input("Ваш выбор (номер): ").strip()
                if choice.isdigit() and 1 <= int(choice) <= len(other_names):
                    return other_names[int(choice) - 1]
            else:
                print("❌ Не удалось найти второго участника.")
                return None
        else:
            return None
    
    def load_chat_data(self, json_path):
        """Загружает JSON-файл переписки (копия вашей функции)"""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Ошибка: файл {json_path} не найден.")
            return None
        except json.JSONDecodeError:
            print(f"Ошибка: файл {json_path} содержит некорректный JSON.")
            return None
    
    def extract_sender_names(self, chat_data):
        """Извлекает уникальные имена отправителей (копия вашей функции)"""
        names = set()
        
        if 'messages' in chat_data:
            for msg in chat_data['messages']:
                sender = msg.get('from') or msg.get('sender') or msg.get('actor')
                if sender and isinstance(sender, str):
                    names.add(sender.strip())
        else:
            if 'members' in chat_data:
                for member in chat_data['members']:
                    name = member.get('name')
                    if name:
                        names.add(name.strip())
            elif 'participants' in chat_data:
                for p in chat_data['participants']:
                    name = p.get('name')
                    if name:
                        names.add(name.strip())
        
        return names
    
    def run_chat_analysis(self, json_path, social_network):
        """Запускает анализ чата для просмотра"""
        print(f"\n📱 Открываю чат из {social_network}...")
        chat_data = self.load_chat_data(Path(json_path))
        
        if chat_data:
            sender_names = self.extract_sender_names(chat_data)
            if sender_names:
                print(f"\n📊 Участники переписки: {', '.join(sorted(sender_names))}")
                if len(sender_names) == 2:
                    print(f"(В переписке участвуют двое: {', '.join(sorted(sender_names))})")
                else:
                    print(f"(Всего уникальных отправителей: {len(sender_names)})")
        
        input("\nНажмите Enter для продолжения...")
    
    def main_menu(self):
        """Главное меню приложения"""
        while True:
            print("\n" + "="*50)
            print("📱 ГЛАВНОЕ МЕНЮ")
            print("="*50)
            print("1. 👤 Мой профиль")
            print("2. 💬 Мои чаты")
            print("0. 🚪 Выход")
            print("="*50)
            
            choice = input("Выберите действие: ").strip()
            
            if choice == '1':
                self.show_profile()
            elif choice == '2':
                self.show_chats()
            elif choice == '0':
                print("\n👋 До свидания!")
                sys.exit(0)
            else:
                print("❌ Неверный выбор. Попробуйте снова.")
    
    def run(self):
        """Запуск приложения"""
        # Спрашиваем имя пользователя
        print("="*50)
        print("🎉 ДОБРО ПОЖАЛОВАТЬ В ЧАТ-МЕНЕДЖЕР!")
        print("="*50)
        
        username = input("\nВведите ваше имя пользователя: ").strip()
        if not username:
            print("❌ Имя не может быть пустым. Попробуйте снова.")
            return
        
        # Загружаем или создаём пользователя
        self.load_user_data()
        
        if not self.current_user or self.current_user.username != username:
            self.current_user = UserProfile(username)
            self.save_user_data()
            print(f"✅ Создан новый профиль для {username}!")
        
        # Запускаем меню
        self.main_menu()

# ========== ЗАПУСК ПРИЛОЖЕНИЯ ==========

if __name__ == "__main__":
    app = ChatApp()
    app.run()
