from aiogram.fsm.state import State, StatesGroup


class CategoryStates(StatesGroup):
    newCategory_state = State()

    updCategory_state_list = State()
    updCategory_state_new = State()

    delCategory_state = State()
    delCategory = State()

    add_product = State()
    add_product_name = State()
    add_product_img = State()
    add_product_category = State()
    edit_product = State()
    edit_name = State()
    edit_photo = State()
    edit_url = State()
    edit_p = State()
    del_product = State()
    del_product_state = State()