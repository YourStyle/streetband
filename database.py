import datetime

import pymongo
from loguru import logger
from typing import Dict, List, Union
import redis
import ujson

import config


class Cache(redis.StrictRedis):
    def __init__(self, host, charset="utf-8", decode_responses=True):
        super(Cache, self).__init__(host,
                                    charset=charset,
                                    decode_responses=decode_responses)
        logger.info("Redis start")

    def jset(self, name, value, ex=3600):
        """функция конвертирует python-объект в Json и сохранит"""
        return self.setex(name, ex, ujson.dumps(value))

    def jget(self, name):
        """функция возвращает Json и конвертирует в python-объект"""
        r = self.get(name)
        if r is None:
            return r
        return ujson.loads(r)


class Database:
    """ Класс работы с базой данных """

    def __init__(self, name):
        self.name = name
        self.client = pymongo.MongoClient("localhost", username='Admin', password='PasswordForMongo63',
                                          authSource='admin', authMechanism='SCRAM-SHA-256')
        self.db = self.client.Street
        logger.info("Database connection established")
        self.musicians = self.db.musicians
        self.users = self.db.users
        self.feedback = self.db.feedback

    def user_exists(self, user_id: str) -> bool:
        return not (self.users.find_one({"user_id": user_id}) is None)

    def musician_exists(self, user_id: str) -> bool:
        return not (self.musicians.find_one({"musician_id": user_id}) is None)

    def feed_exists(self, feed_id: str) -> bool:
        return not (self.feedback.find_one({"feed_id": feed_id}) is None)

    def add_user(self, user_id: str, name=None, language="ru"):
        if not self.user_exists(user_id):
            n_user = {"user_id": user_id, "musician": False, "fav_genres": [], "fav_groups": [], "city": None,
                      "pending": {}, "sub_mailing": True}
            self.users.insert_one(n_user)

    def add_musician(self, user_id: str):
        if not self.musician_exists(user_id):
            n_musician = {"musician_id": user_id, 'musician_name': None, "group_pic": None,
                          'group_genre': [], "group_description": None, "group_leader": None, "current_location": None,
                          'subscription': None, 'free_subscription': None, 'active_subscription': None, 'songs': []}
            self.musicians.insert_one(n_musician)

            if not self.user_exists(user_id):
                self.add_user(user_id)

            self.users.update_one({"user_id": user_id}, {"$set": {'musician': True}})

            # {'group_name': 'Кек',
            # 'group_requisites': '4276 6600 3705 5514',
            # 'group_pic': 'AgACAgIAAxkDAAIF5mH1MMAf1G9P_mwRyk5avg34Kmq5AAIutzEbibypSx8OsdsjZRVeAQADAgADeQADIwQ',
            # 'group_genre': жанры
            # 'group_description': 'Мом',
            # 'group_leader': '@DeadGleb'

    def add_feedback_text(self, feed_id: str, comment: str = None):
        if self.feed_exists(feed_id):
            self.feedback.update_one({"feed_id": feed_id}, {"$set": {"text": comment}})
        else:
            feedback = {"feed_id": feed_id, "text": comment}
            self.feedback.insert_one(feedback)

    def add_feedback_rate(self, feed_id: str, rate: int = None):
        if self.feed_exists(feed_id):
            self.feedback.update_one({"feed_id": feed_id}, {"$set": {"stars": rate}})
        else:
            feedback = {"feed_id": feed_id, "stars": rate}
            self.feedback.insert_one(feedback)

    def show_feedback(self, feed_id):
        return self.feedback.find_one({"feed_id": feed_id}, projection={"_id": False})

    def show_feedbacks(self):
        return list(self.feedback.find(projection={"_id": False, "subscription": False}))

    def set_m_name(self, user_id: str, musician_name: str):
        self.musicians.update_one({"musician_id": user_id}, {"$set": {"musician_name": musician_name}})

    def set_group_pic(self, user_id: str, group_pic: str):
        self.musicians.update_one({"musician_id": user_id}, {"$set": {"group_pic": group_pic}})

    def set_group_description(self, user_id: str, group_description: str):
        self.musicians.update_one({"musician_id": user_id}, {"$set": {"group_description": group_description}})

    def set_group_leader(self, user_id: str, group_leader: str):
        self.musicians.update_one({"musician_id": user_id}, {"$set": {"group_leader": group_leader}})

    def set_group_genre(self, user_id: str, genres: List[str]):
        genres_id = []
        for genre in genres:
            for k, v in config.GENRES.items():
                if v == genre:
                    genres_id.append(k)
        self.musicians.update_one({"musician_id": user_id}, {"$set": {"group_genre": genres_id}})

    def set_group_current_location(self, user_id: str, location: Union[Dict, None]):
        self.musicians.update_one({"musician_id": user_id}, {"$set": {"current_location": location}})

    def get_musician(self, user_id: str) -> Dict:
        return self.musicians.find_one({"musician_id": user_id}, projection={"_id": False})

    def get_musicians(self):
        buffer = list(self.musicians.find(projection={"_id": False, "subscription": False, "free_subscription": False}))
        if cache.jget("musicians") != buffer:
            cache.jset("musicians", buffer)

    def get_user(self, user_id: str) -> Dict:
        return self.users.find_one({"user_id": user_id})

    def get_users(self):
        buffer = list(self.users.find(projection={"_id": False}))
        print(buffer)
        if cache.jget("users_data") != buffer:
            cache.jset("users_data", buffer)

    def is_musician(self, user_id: str) -> bool:
        return self.users.find_one({"user_id": user_id})["musician"]

    def to_fav(self, user_id: str, musician_id: str):
        c_user = self.get_user(user_id)
        if musician_id not in c_user["fav_groups"]:
            update = self.users.update_one({"user_id": user_id}, {"$push": {"fav_groups": musician_id}})
            c_user_pending = c_user["pending"]
            c_mus = self.get_musician(musician_id)
            m_genres = c_mus["group_genre"]
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

    def from_fav(self, user_id: str, musician_id: str):
        self.users.update_one({"user_id": user_id}, {"$pull": {"fav_groups": musician_id}})

    def add_genre(self, user_id: str, genres: List[str]):
        c_genres = self.users.find_one({"user_id": user_id})["fav_genres"]
        # print(genres)
        for i in genres:
            if i not in c_genres:
                self.users.update_one({"user_id": user_id}, {"$push": {"fav_genres": i}})

    def add_m_genre(self, user_id: str, genres: List[str]):
        c_genres = self.musicians.find_one({"musician_id": user_id})["group_genre"]
        for i in genres:
            if i not in c_genres:
                self.musicians.update_one({"musician_id": user_id}, {"$push": {"group_genre": i}})

    def free_subscription(self, musician_id: str):
        self.musicians.update_one({"musician_id": musician_id},
                                  {"$set": {"free_subscription": datetime.datetime.now() + datetime.timedelta(days=91),
                                            "active_subscription": True}})

    # def end_free_subscription(self, musician_id: str):
    #     if self.get_subscription(musician_id):
    #         self.musicians.update_one({"musician_id": musician_id},
    #                                   {"$set": {"free_subscription": None, "active_subscription": True}})
    #     else:
    #         self.musicians.update_one({"musician_id": musician_id},
    #                                   {"$set": {"free_subscription": None, "active_subscription": False}})

    def end_subscription(self, musician_id: str):
        remain = self.get_subscription(musician_id)
        if remain.days == 0:
            self.musicians.update_one({"musician_id": musician_id},
                                      {"$set": {"subscription": None, "active_subscription": False}})

    def get_subscription(self, musician_id: str):
        sub = self.musicians.find_one({"musician_id": musician_id})['subscription']
        print(sub)
        if sub is None:
            return None
        else:
            return sub - datetime.datetime.now()

    def get_free_subscription(self, musician_id: str):
        sub = self.musicians.find_one({"musician_id": musician_id})["free_subscription"]
        if sub is None:
            return None
        else:
            return sub - datetime.datetime.now()

    def cancel_subscription(self, musician_id: str):
        if (self.get_subscription(musician_id) or self.get_free_subscription(musician_id)) is not None:
            self.musicians.update_one({"musician_id": musician_id},
                                      {"$set": {"subscription": None, "free_subscription": None,
                                                "active_subscription": False}})

    def activate_subscription(self, musician_id: str):
        self.musicians.update_one({"musician_id": musician_id},
                                  {"$set": {"subscription": datetime.datetime.now() + datetime.timedelta(days=31),
                                            "active_subscription": True}})

    def add_song(self, user_id: str, file_id: str, title: str):
        self.musicians.update_one({"musician_id": user_id}, {"$push": {"songs": [title, file_id]}})

    def delete_song(self, user_id: str, song: list):
        self.musicians.update_one({"musician_id": user_id}, {"$pull": {"songs": song}})

    def delete_songs(self, user_id: str):
        mus_songs = self.get_songs(user_id)
        for i in mus_songs:
            self.musicians.update_one({"musician_id": user_id}, {"$pull": {"songs": i}})

    def get_songs(self, user_id: str):
        return self.musicians.find_one({"musician_id": user_id})['songs']

    def delete_genres(self, user_id: str):
        c_genres = self.users.find_one({"user_id": user_id})["fav_genres"]
        for i in c_genres:
            self.users.update_one({"user_id": user_id}, {"$pull": {"fav_genres": i}})

    def delete_m_genres(self, user_id: str):
        c_genres = self.musicians.find_one({"musician_id": user_id})["group_genre"]
        for i in c_genres:
            self.musicians.update_one({"musician_id": user_id}, {"$pull": {"group_genre": i}})

    def delete_users(self, user_id: str):
        if self.user_exists(user_id):
            self.users.delete_one({"user_id": user_id})

    def delete_musician(self, user_id: str):
        if self.musician_exists(user_id):
            self.musicians.delete_one({"musician_id": user_id})

    def set_mailing_status(self, user_id: str):
        return self.users.update_one({"user_id": user_id}, {"$set": {"sub_mailing": True}})

    def check_mail_status(self, user_id: str):
        return self.users.find_one({"user_id": user_id})["sub_mailing"]

    def stop_mailing(self, user_id: str):
        self.users.update_one({"user_id": user_id}, {"$push": {"sub_mailing": False}})


cache = Cache(
    host=config.REDIS_HOST,
)
database = Database("Street")
