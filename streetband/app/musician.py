import typing

from aiogram.dispatcher.filters import BoundFilter

from streetband.database import cache


class MusicianFilter(BoundFilter):
    key = 'is_musician'

    def __init__(self, is_musician: typing.Optional[bool] = None):
        self.is_musician = is_musician

    async def check(self, obj):
        # print(obj)
        if self.is_musician is None:
            return False
        musicians = cache.jget("musicians")
        ids = []
        for musician in musicians:
            ids.append(int(musician["musician_id"]))
        return obj.from_user.id in ids

