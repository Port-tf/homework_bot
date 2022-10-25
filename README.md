Telegram bot для проверки статуса домашней работы на ЯндексПрактикуме.
Возможности бота:
Раз в 10 минут опрашивает API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы.
При обновлении статуса анализирует ответ API и отправляет вам соответствующее уведомление в Telegram.
Логгирует свою работу и сообщает вам о важных проблемах сообщением в Telegram.
Технологии
Python 3.9.8
API

Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:

git clone https://github.com/mityasun/homework_bot.git
cd homework_bot
Cоздать и активировать виртуальное окружение:

python -m venv env
source env/bin/activate
Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```
Укажите собственные токены:

Создать файл .env в директории проекта и пропишите в нем:
PRACTICUM_TOKEN = токен Яндекс практикум.
TELEGRAM_TOKEN = токен Telegram полученный от BotFather.
TELEGRAM_CHAT_ID = id вашего чата в Telegram.
Запустить проект:

python homework.py
Получаем токены:
Зарегистрируйте бота в BotFather:
Регистрация бота и получение токена

Получите токен в ЯндексПрактикум:
Получить токен

Получите id своего чата у бота Userinfobot:
Получить свой id
