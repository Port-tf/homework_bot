import logging
import os
import sys
import time
from datetime import datetime
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telegram import Bot
from telegram.error import TelegramError

from exceptions import (EmptyResponseFromAPI, IncorrectResponseCode,
                        NotForShipment, TelegramCustomError)

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PRACTICUM_TOKEN = os.getenv('PRACTIC_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGA_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGA_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICT = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.',
}


def send_message(bot, message):
    """
    Отправляет сообщение в Telegram чат.
    Определяется переменной окружения TELEGRAM_CHAT_ID.
    """
    try:
        logging.info('Отправка сообщения инициализирована')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except TelegramError as error:
        raise TelegramCustomError(
            f'Сбой при отправке сообщения в Телеграмм: {error}')
    else:
        logging.info('Cообщение отправлено в Телеграмм')


def get_api_answer(current_timestamp):
    """
    Запрос к эндпоинту API-сервиса.
    В качестве параметра функция получает временную метку.
    В случае успешного запроса должна вернуть ответ API,
    преобразовав его из формата JSON к типам данных Python.
    """
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    param_request = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': params,
    }
    logging.info('Начался запрос к API')

    try:
        response = requests.get(**param_request)
        if response.status_code != HTTPStatus.OK:
            raise IncorrectResponseCode(
                'Ошибка: {}, HTTPStatus: {}, текст: {}.'.format(
                    response.status_code, response.reason, response.text))
        return response.json()

    except ConnectionError:
        raise ConnectionError('Ошибка при запросе к основному API: '
                              '{url}{headers}{params}'.format(**param_request)
                              )


def check_response(response):
    """
    Проверяет ответ API на корректность.
    Если ответ API соответствует ожиданиям, то функция должна вернуть
    список домашних работ, доступный в ответе API по ключу 'homeworks'.
    """
    logging.info('Начало проверки ответа сервера')
    if not isinstance(response, dict):
        raise TypeError(
            'Ответ API не словарь'
        )
    if ('homeworks' or 'current_date') not in response:
        raise EmptyResponseFromAPI('Ответ API пришел пустой')
    homework = response.get('homeworks')
    if not isinstance(homework, list):
        raise KeyError(
            "Ответ API: response['homeworks'] не список"
        )
    return homework


def parse_status(homework):
    """
    Извлекает из информации о конкретной домашней работе статус этой работы.
    В качестве параметра функция получает только один элемент
    из списка домашних работ. В случае успеха, функция возвращает
    подготовленную для отправки в Telegram строку,
    содержащую один из вердиктов словаря HOMEWORK_STATUSES.
    """
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if 'homework_name' not in homework:
        raise KeyError(
            'Отсутствует ключ "homework_name" в ответе API'
        )
    if homework_status not in HOMEWORK_VERDICT:
        raise ValueError(f'Неизвестный статус работы: {homework_status}')
    return (
        'Изменился статус проверки работы "{}". Статус: {},'.format(
            homework_name, HOMEWORK_VERDICT[homework_status]
        )
    )


def check_tokens():
    """
    Проверяет доступность переменных окружения.
    Они необходимы для работы программы.
    """
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    current_timestamp = int(time.time())
    prev_report = dict()
    current_report = dict()
    if not check_tokens():
        logging.critical('Проверьте переменные окружения')
        sys.exit('Проверьте переменные окружения')
    bot = Bot(token=TELEGRAM_TOKEN)

    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if homework:
                last_homework = homework[0]
                current_report['name'] = last_homework['homework_name']
                message_parse = parse_status(last_homework)
                current_report['comment'] = last_homework['reviewer_comment']
                message = ('{} Комментарий к работе: {}.'.format(
                    message_parse, last_homework['reviewer_comment']))
                current_report['message'] = message
            else:
                prev_time = datetime.fromtimestamp(current_timestamp)
                current_report['message'] = (
                    'до настоящего момента домашних работ нет.')
                message = 'За период c {} {}'.format(
                    prev_time, current_report['message'])
            if current_report != prev_report:
                send_message(bot, message)
                prev_report = current_report.copy()
            else:
                logging.debug('Новых статусов нет')

        except NotForShipment as error:
            logging.error(f'{error}')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            current_report['message'] = message
            logging.error(f'Сбой в работе программы: {error}')
            if current_report != prev_report:
                send_message(bot, message)
                prev_report = current_report.copy()

        finally:
            current_timestamp = response.get('current_date', current_timestamp)
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        handlers=[
            logging.FileHandler(
                f'{BASE_DIR}\\my_homework.log', encoding='UTF-8', mode='w'),
            logging.StreamHandler(sys.stdout)
        ],
        format=(
            '%(asctime)s, %(levelname)s, %(message)s : '
            '%(filename)s(%(funcName)s):%(lineno)d'
        )
    )
    main()
