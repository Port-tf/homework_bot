import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTIC_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGA_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGA_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('my_homework.log', encoding='UTF-8')
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.addHandler(file_handler)


def send_message(bot, message):
    """
    Отправляет сообщение в Telegram чат.
    Определяется переменной окружения TELEGRAM_CHAT_ID.
    """
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.info('Удачная отправка сообщения')
    except Exception:
        logger.error('Сбой при отправке сообщения')
        raise Exception('Сбой при отправке сообщения')


def get_api_answer(current_timestamp):
    """
    Запрос к эндпоинту API-сервиса.
    В качестве параметра функция получает временную метку.
    В случае успешного запроса должна вернуть ответ API,
    преобразовав его из формата JSON к типам данных Python.
    """
    try:
        timestamp = current_timestamp or int(time.time())
        params = {'from_date': timestamp}
        response = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if response.status_code != HTTPStatus.OK:
            raise Exception('Ошибка HTTPStatus')
        else:
            return response.json()
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        raise Exception(f'Ошибка при запросе к основному API: {error}')


def check_response(response):
    """
    Проверяет ответ API на корректность.
    Если ответ API соответствует ожиданиям, то функция должна вернуть
    список домашних работ, доступный в ответе API по ключу 'homeworks'.
    """
    if type(response) is not dict:
        raise TypeError(
            'Ответ API не словарь'
        )
    try:
        homework = response['homeworks']
        if type(homework) is not list:
            raise TypeError(
                'Ответ API homeworks не список'
            )
        return homework
    except Exception:
        logging.error('Не найден ключ "homeworks"')
        raise Exception('Не найден ключ "homeworks"')


def parse_status(homework):
    """
    Извлекает из информации о конкретной домашней работе статус этой работы.
    В качестве параметра функция получает только один элемент
    из списка домашних работ. В случае успеха, функция возвращает
    подготовленную для отправки в Telegram строку,
    содержащую один из вердиктов словаря HOMEWORK_STATUSES.
    """
    homework_name = homework['homework_name']
    homework_status = homework['status']
    verdict = HOMEWORK_STATUSES[homework_status]
    if homework_status not in HOMEWORK_STATUSES:
        logging.error(f'Неизвестный статус работы: {homework_status}')
        raise Exception(f'Неизвестный статус работы: {homework_status}')
    return (
        f'Изменился статус проверки работы "{homework_name}". {verdict}')


def check_tokens():
    """
    Проверяет доступность переменных окружения.
    Они необходимы для работы программы.
    """
    try:
        if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            return True
        else:
            return False
    except Exception:
        logger.error(
            'Проверьте переменные окружения')
        raise Exception(
            'Проверьте переменные окружения')


def main():
    """Основная логика работы бота."""
    bot = Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    status = ''
    trus = check_tokens()

    while trus:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get('current_date')
            homework = check_response(response)
            if len(homework) == 0:
                logging.debug('Новых статусов нет')
            else:
                message = parse_status(homework[0])
                send_message(bot, message)
            time.sleep(RETRY_TIME)

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.critical(f'Сбой в работе программы: {error}')
            if status != message:
                send_message(bot, message)
                status = message
                raise Exception(f'Сбой в работе программы: {error}')
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
