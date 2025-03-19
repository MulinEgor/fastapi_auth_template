"""Модуль для работы с хеш-функциями."""

import hashlib


class HashService:
    """Класс для работы с хеш-функциями."""

    def generate(input: str) -> str:
        """
        Сгенерировать хэш строки.

        Args:
            input (str): Строка для хэширования.

        Returns:
            str: Хэш строки.
        """
        return hashlib.sha256(input.encode()).hexdigest()
