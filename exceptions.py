class NotForShipment(Exception):
    """Исключения не для отправки."""

    pass


class TelegramCustomError(NotForShipment):
    """Выбрасываем кастомное исключение ТелеграмЕррор."""

    pass


class IncorrectResponseCode(Exception):
    """ИсклюНеВерныйКодОтвета."""

    pass


class EmptyResponseFromAPI(NotForShipment):
    """Исключение: получил пустой ответ от API."""

    pass
