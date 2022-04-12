from aiogram.utils.callback_data import CallbackData

location_callback = CallbackData("find", "location", "artist_id")
user_reg_callback = CallbackData("reg", "user")
choice_callback = CallbackData("choose", "decision")
action_callback = CallbackData("cur", "action", "id")
groups_callback = CallbackData("group", "location")
info_callback = CallbackData("info", "id", "db_number")
add_callback = CallbackData("add", "id", "db_number")
donate_callback = CallbackData("donate", "id")
delete_callback = CallbackData("add", "id")
fav_callback = CallbackData("fav", "id")
review_callback = CallbackData("review", "score")
songs_callback = CallbackData("songs", "id")
