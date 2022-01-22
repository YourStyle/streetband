from typing import List

from loguru import logger


class Database:
    """ Класс работы с базой данных """

    def __init__(self, name):
        self.name = name
        # self._conn = self.connection()
        logger.info("Database connection established")

    def add_user(self, user_id: str, name=None, language="ru"):
        pass

    def get_musician(self, musician_id: str) -> List:
        pass

    def user_exists(self, user_id: str) -> bool:
        pass


database = Database("users")
