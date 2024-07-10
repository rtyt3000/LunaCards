import os
import subprocess
import telebot
from telebot import types
import json

config = {}

def get_config():
    with open('config2.json', 'r') as file:
        global config
        config = json.loads(file.read())

bot = telebot.TeleBot(config['service_bot_api_key'])


script_process = None
tech_script_process = None

# Команда для запуска скрипта
@bot.message_handler(commands=['start_bot'])
def start_bot(message):
    if message.user.id in config['allowed_users'] or len(config['allowed_users']) == 0:
        global script_process
        if script_process is None:
            script_process = subprocess.Popen(["python", config['main_bot_direction']])
            bot.reply_to(message, "Скрипт main.py запущен.")
        else:
            bot.reply_to(message, "Скрипт уже запущен.")
    else:
        bot.send_message(message.user.id, f"У вас недостаточно прав для данного действия")



# Команда для остановки скрипта
@bot.message_handler(commands=['stop_bot'])
def stop_bot(message):
    if message.user.id in config['allowed_users'] or len(config['allowed_users']) == 0:
        global script_process
        if script_process is not None:
            script_process.terminate()
            script_process = None
            bot.reply_to(message, "Скрипт main.py остановлен.")
        else:
            bot.reply_to(message, "Скрипт не запущен.")
    else:
        bot.send_message(message.user.id, f"У вас недостаточно прав для данного действия")


@bot.message_handler(commands=['start_tech'])
def start_tech(message):
    if message.user.id in config['allowed_users'] or len(config['allowed_users']) == 0:
        global tech_script_process
        if tech_script_process is None:
            tech_script_process = subprocess.Popen(["python", config['tech_bot_direction']])
            bot.reply_to(message, "Режим тех перерыва включен")
        else:
            bot.reply_to(message, "Режим тех перерыва уже был включен")
    else:
        bot.send_message(message.user.id, f"У вас недостаточно прав для данного действия")

@bot.message_handler(commands=['stop_tech'])
def stop_tech(message):
    if message.user.id in config['allowed_users'] or len(config['allowed_users']) == 0:
        global tech_script_process
        if tech_script_process is not None:
            tech_script_process.terminate()
            tech_script_process = None
            bot.reply_to(message, "Режим тех перерыва выключен")
        else:
            bot.reply_to(message, "Режим тех перерыва не включен")
    else:
        bot.send_message(message.user.id, f"У вас недостаточно прав для данного действия")


# Команда для показа файлов в директории
@bot.message_handler(commands=['show'])
def show_files(message):
    if message.user.id in config['allowed_users'] or len(config['allowed_users']) == 0:
        files = os.listdir(".")
        files_list = "\n".join(files)
        bot.reply_to(message, f"Файлы в директории:\n{files_list}")
    else:
        bot.send_message(message.user.id, f"У вас недостаточно прав для данного действия")



# Команда для получения файла
@bot.message_handler(commands=['get'])
def get_file(message):
    try:
        if message.user.id in config['allowed_users'] or len(config['allowed_users']) == 0:
            filename = message.text.split()[1]
            if os.path.exists(filename):
                with open(filename, 'rb') as file:
                    bot.send_document(message.chat.id, file)
            else:
                bot.reply_to(message, "Файл не найден")
        else:
            bot.send_message(message.user.id, f"У вас недостаточно прав для данного действия")

    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите имя файла")


# Команда для удаления файла
@bot.message_handler(commands=['del'])
def delete_file(message):
    try:
        if message.user.id in config['allowed_users'] or len(config['allowed_users']) == 0:
            filename = message.text.split()[1]
            if os.path.exists(filename):
                os.remove(filename)
                bot.reply_to(message, f"Файл {filename} удален")
            else:
                bot.reply_to(message, "Файл не найден")
        else:
            bot.send_message(message.user.id, f"У вас недостаточно прав для данного действия")

    except IndexError:
        bot.reply_to(message, "Пожалуйста, укажите имя файла")

@bot.message_handler(commands=['update_config'])
def update_config(message):
    try:
        if message.user.id in config['allowed_users'] or len(config['allowed_users']) == 0:
            get_config()
            bot.send_message(message.user.id, f"Вы успешно изменили настройки бота. Если вы изменили api ключ данного бота, пожадуйста перезапустите этот скрипт, чтобы изминения вступили в силу")
        else:
            bot.send_message(message.user.id, f"У вас недостаточно прав для данного действия")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")

@bot.message_handler(commands=['/help'])
def show_help(message):
    if message.user.id in config['allowed_users'] or len(config['allowed_users']) == 0:
        bot.send_message(message.user.id, 'Список комманд бота:\n/start_bot - запускает основного бота\n/stop_bot - останавливает основного бота\n/start_tech - запускает бота для тех перерывов\n/stop_tech - останавливает бота для тех перерывов\n/show - показывает все файлы в директории\n/get {название файла} - выгружвет указанный файл\n/del {название файла} - удаляет указанный файл\n/update_config - обновляет конфиг файл (используйте если вы изменили конфиг этого бота)\n/help_config - справка по конфиг файлу\n\nРазрабочтик @neheofen')
    else:
        bot.send_message(message.user.id, f"У вас недостаточно прав для данного действия")


@bot.message_handler(commands=['/help_config'])
def show_help(message):
    if message.user.id in config['allowed_users'] or len(config['allowed_users']) == 0:
        bot.send_message(message.user.id, 'Значения используемые в конфиг файле:\nservice_bot_api_key - апи ключ самого бота\ntech_bot_api_key - апи ключ самого бота, используется во время тех перерывов\nmain_bot_direction - расположение главного файла основного бота\ntech_bot_direction - расположение файла бота бота для тех перерывов\ncommands - команды использумые в основном боте\nstartwith_commands -  команды, имеющие доп аргумент, использумые в основном боте\nallowed_users - пользователи, которые имеют возможность использовать этого бота (если массив пустой, то все могут пользоваться)')
    else:
        bot.send_message(message.user.id, f"У вас недостаточно прав для данного действия")

@bot.message_handler(commands=['/start'])
def start(message):
    bot.send_message(message.user.id, f"Добро пожаловать в бота для обслуживания других ботов. Пропишите /help, что-бы узнать список комманд")


# Обработка добавления файла
@bot.message_handler(content_types=['document'])
def add_file(message):
    try:
        if message.user.id in config['allowed_users'] or len(config['allowed_users']) == 0:
            file_info = bot.get_file(message.document.file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            with open(message.document.file_name, 'wb') as new_file:
                new_file.write(downloaded_file)

            bot.reply_to(message, f"Файл {message.document.file_name} добавлен/обновлен")
        else:
            bot.send_message(message.user.id, f"У вас недостаточно прав для данного действия")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")


# Запуск бота
bot.polling()
