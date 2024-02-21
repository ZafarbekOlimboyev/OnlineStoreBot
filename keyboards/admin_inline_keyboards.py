from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import DB_NAME
from utils.database import Database


db = Database(DB_NAME)


# Function for make inline keyboards from category names
def make_category_list() -> InlineKeyboardMarkup:
    categories = db.get_categories()
    rows = []
    for category in categories:
        rows.append([
            InlineKeyboardButton(
                text=str(category[1]),
                callback_data=str(category[1])
            )
        ])
    kb_categories = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb_categories

def make_product_list() -> InlineKeyboardMarkup:
    products = db.get_products()
    rows = []
    for product in products:
        rows += product
    kb_products = InlineKeyboardMarkup(inline_keyboard=rows)
    return kb_products


yes_or_no = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Yes",callback_data="yes")],
    [InlineKeyboardButton(text="No",callback_data="no")]
])

product_edit = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="name",callback_data="name")],
    [InlineKeyboardButton(text="photo",callback_data="photo")],
    [InlineKeyboardButton(text="category",callback_data="category")]
])