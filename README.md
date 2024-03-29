# Telegram bot для проверки статуса домашней работы на Яндекс.Практикуме.
### Возможности бота:
Раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы.\
При обновлении статуса анализирует ответ API, если статус изменился и отправляет вам соответствующее уведомление в Telegram.\
Логгирует свою работу и сообщает вам о важных проблемах сообщением в Telegram.\

### Технологии:
Python 3.9.8\
API

### Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:
```
git clone https://github.com/Port-tf/homework_bot.git
```
Cоздать и активировать виртуальное окружение:
```
python -m venv env
source env/bin/activate
```
Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
python -m pip install --upgrade pip
```
Укажите собственные токены:

Создать файл .env в директории проекта и пропишите в нем:\
PRACTICUM_TOKEN = токен Яндекс.Практикум.\
TELEGRAM_TOKEN = токен Telegram полученный от BotFather.\
TELEGRAM_CHAT_ID = ID вашего чата в Telegram.

Запустить проект:
```
python homework.py
```
