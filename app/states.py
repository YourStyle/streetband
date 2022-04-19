from aiogram.dispatcher.filters.state import StatesGroup, State


class RegistrationUser(StatesGroup):
    Agreeing_terms = State()


class RegistrationMusician(StatesGroup):
    Agreeing_terms = State()
    Group_name = State()
    Requisites = State()
    Group_pic = State()
    Group_genres = State()
    Group_desc = State()
    Waiting_first_approve = State()
    Uploading_agreement = State()
    Waiting_final_approve = State()


class ChoosingMusician(StatesGroup):
    Choosing_musician = State()


class EditingProfile(StatesGroup):
    EditingName = State()
    EditingPic = State()
    EditingDesc = State()
    EditingLeader = State()
    EditingGenres = State()


class Donating(StatesGroup):
    UserDonating = State()


class Subscribing(StatesGroup):
    MusicianSubscribing = State()
    MusicianPaid = State()


class Feedback(StatesGroup):
    Reviewing = State()
