from aiogram.dispatcher.filters.state import StatesGroup, State


class Registration_User(StatesGroup):
    Agreeing_terms = State()


class Registration_Musician(StatesGroup):
    Agreeing_terms = State()
    Group_name = State()
    Requisites = State()
    Group_pic = State()
    Group_desc = State()
    Waiting_first_approve = State()
    Uploading_agreement = State()
    Waiting_final_approve = State()

class Choosing_Musician(StatesGroup):
    Choosing_musician = State()