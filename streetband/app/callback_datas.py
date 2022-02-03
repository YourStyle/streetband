from aiogram.utils.callback_data import CallbackData

location_callback = CallbackData("find", "location", "artist_id")
user_reg_callback = CallbackData("reg", "user")
choice_callback = CallbackData("choose", "decision")
action_callback = CallbackData("cur", "action", "id")
groups_callback = CallbackData("group", "location")
info_callback = CallbackData("info", "id", "db_loc")
add_callback = CallbackData("add", "id", "db_loc")
