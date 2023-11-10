from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

monday = InlineKeyboardButton(text="Понедельник", callback_data="Понедельник")
tuesday = InlineKeyboardButton(text="Вторник", callback_data="Вторник")
wednesday = InlineKeyboardButton(text="Среда", callback_data="Среда")
thursday = InlineKeyboardButton(text="Четверг", callback_data="Четверг")
friday = InlineKeyboardButton(text="Пятница", callback_data="Пятница")
saturday = InlineKeyboardButton(text="Суббота", callback_data="Суббота")
days_of_week = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]


change_group = InlineKeyboardButton(text="Изменить группу", callback_data="change_group")

day_of_week_inline_keyboard = InlineKeyboardMarkup(inline_keyboard=[[monday, tuesday, wednesday], [thursday, friday, saturday], [change_group]])

cancel_button = InlineKeyboardButton(text="Отмена", callback_data="cancel")
cancel_menu = InlineKeyboardMarkup(inline_keyboard=[[cancel_button]])

# Feedback

yes = InlineKeyboardButton(text="Да 👍", callback_data="yes")
no = InlineKeyboardButton(text="Нет 💩", callback_data="no")
feedback_menu = InlineKeyboardMarkup(inline_keyboard=[[yes, no]])

