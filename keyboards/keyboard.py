from aiogram.types import ReplyKeyboardMarkup,KeyboardButton

cancel = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="cancel")]
],
    resize_keyboard=True,
    input_field_placeholder="If you want cancel, touch the 'cencel' button"
)