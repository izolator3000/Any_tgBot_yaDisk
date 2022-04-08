from telebot import TeleBot, types
from requests import get
from random import randint
from yadisk import YaDisk
from config import config


bot = TeleBot(config["tgTOKEN"])
disk = YaDisk(token=config["yaTOKEN"])


@bot.message_handler(commands=['start', 'help'])
def start_end(message):
    bot.send_message(message.chat.id, "Добрый день! Какой номер Вашей сделки?")


@bot.message_handler(content_types=['text'])
def get_delay_number(message):
    if is_delay_number(message.text):
        answer_deal(message)
    else:
        bot.reply_to(message, "Такого номера сделки нет в моей базе данных")


def is_delay_number(delay_number):
    """
    Проверка на то, является ли delay_number числом.

    Где-то, скорее всего в таблице .xlsx, хранятся номера сделок.
    Бот будет считывать номера сделок из файла и сверять с номером,
    переданным клиентом.
    """
    # TODO Из бд находить или не находить сделку
    return False if int(delay_number) < 1000 else True     # Заглушка


def answer_deal(message):
    """
    Если сделки ещё не было, то отвечаем приветствием и инструкцией,
    Если сделка уже была, то отвечаем напоминанием.
    После обоих исходов назначаем текущий документ
    """
    bot.reply_to(message, "Для совершения Вашей сделки нужны следующие документы:\n"
                          "Паспорт\nСвидетельство о жизни\nИ т.д.\n...\n"
                          "Сейчас я буду спрашивать у Вас эти документы по очереди.\n"
                          "Если какого-то документа у Вас сейчас нет - пропустите "
                          "этот пункт и пришлёте, когда будете готовы.")
    get_next_document(message)
    # TODO Разделение диалога, если оно всё ещё нужно. Сейчас не уверен уже


def get_next_document(document):
    change_current_document_for_deal(document.text)
    skip_document_markup = types.InlineKeyboardMarkup()
    item_skip = types.InlineKeyboardButton(text="Заполнить позже", callback_data="skip")
    skip_document_markup.add(item_skip)
    # TODO Узнать, можно ли сократить создание одной кнопки по количеству кода
    bot.send_message(document.chat.id, f"Пришлите, пожалуйста {current_document()}",
                     reply_markup=skip_document_markup)


def change_current_document_for_deal(deal_number: str):
    """
    Записывает следующий по списку документов для текущей сделки
    """
    # TODO По номеру сделки находит следующий документ из БД и сохраняет его в файл
    open("current_document.txt", 'w').write(f"Документ по имени {randint(1, 100)}")     # Заглушка


@bot.message_handler(content_types=['document'])
def get_document(document):
    if current_document() != "":
        upload_document(document)
        get_next_document(document)
    else:
        bot.reply_to(document, "Подождите, пожалуйста. Я не просил Вас что-либо загружать")


def current_document():
    try:
        return open('current_document.txt', 'r').read()
    except FileNotFoundError:
        raise FileNotFoundError("Файл с текущим документом не найден")


def upload_document(message):
    """
    Загружает документ на ЯД
    """
    # TODO Создавать папки и загружать файл не просто на диск, а в соответствующую директорию
    try:
        file_info = bot.get_file(message.document.file_id)
        file = get('https://api.telegram.org/file/bot{0}/{1}'.format(config["tgTOKEN"], file_info.file_path))
        open("upload.txt", 'w').write(file.text)
        disk.upload("upload.txt", f"/{current_document()}.txt")
    except:
        bot.send_message(message.chat.id, "Документ не загружен")
    else:
        bot.send_message(message.chat.id, "Документ загружен")


@bot.callback_query_handler(func=lambda call: call.data == "skip")
def skip_document(call):
    get_next_document(call.message)


bot.infinity_polling()
