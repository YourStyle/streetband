import pymongo
from loguru import logger
from typing import Dict, List
import redis
import ujson

import config


class Cache(redis.StrictRedis):
    def __init__(self, host, port, password, charset="utf-8", decode_responses=True):
        super(Cache, self).__init__(host, port,
                                    password=password,
                                    charset=charset,
                                    decode_responses=decode_responses)
        logger.info("Redis start")

    def jset(self, name, value, ex=0):
        """функция конвертирует python-объект в Json и сохранит"""
        r = self.get(name)
        if r is None:
            return r
        return ujson.loads(r)

    def jget(self, name):
        """функция возвращает Json и конвертирует в python-объект"""
        return ujson.loads(self.get(name))


class Database:
    """ Класс работы с базой данных """

    def __init__(self, name):
        self.name = name
        # self._conn = self.connection()
        self.client = pymongo.MongoClient()
        self.db = self.client.Street
        logger.info("Database connection established")
        self.musicians = self.db.musicians
        self.users = self.db.users

    def user_exists(self, user_id: str) -> bool:
        return not (self.users.find_one({"user_id": user_id}) is None)

    def musician_exists(self, user_id: str) -> bool:
        return not (self.musicians.find_one({"user_id": user_id}) is None)

    def add_user(self, user_id: str, name=None, language="ru"):
        if not self.user_exists(user_id):
            n_user = {"user_id": user_id, "musician": False, "fav_genres": [], "fav_groups": [], "city": None,
                      "pending": {}}
            self.users.insert_one(n_user)

    def get_musician(self, musician_id: str) -> Dict:
        return self.musicians.find_one({"user_id": musician_id})

    def insert_or_update_users(self, user_id: str, genres: List):
        pass

    def get_user(self, musician_id: str) -> Dict:
        return self.users.find_one({"user_id": musician_id})

    def is_musician(self, user_id: str) -> bool:
        return self.users.find_one({"user_id": user_id})["musician"]

    def to_fav(self, user_id: str, musician_id: str):
        self.users.update_one({"user_id": user_id}, {"$push": {"fav_groups": musician_id}})
        c_user = self.users.find_one({"user_id": user_id})
        c_user_pending = c_user["pending"]
        m_genres = self.musicians.find_one({"user_id": user_id})["genres"]
        for i in m_genres:
            if i not in c_user["fav_genres"]:
                try:
                    c_user_pending[i] += 1
                except KeyError:
                    c_user_pending[i] = 1
                if c_user_pending[i] == config.PENDING_APPROVAL:
                    self.users.update_one({"user_id": user_id}, {"$push": {"fav_genres": i}})
                    c_user_pending.pop(i, None)
        self.users.update_one({"user_id": user_id}, {"$set": {"pending": c_user_pending}})

    def delete_users(self, user_id: str):
        if self.user_exists(user_id):
            self.users.delete_one({user_id: user_id})

    def delete_musician(self, user_id: str):
        if self.musician_exists(user_id):
            self.musicians.delete_one({"user_id": user_id})


cache = Cache(
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
    password=config.REDIS_PASSWORD
)
database = Database("Street")
