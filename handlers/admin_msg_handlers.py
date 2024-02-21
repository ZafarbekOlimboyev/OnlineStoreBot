from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery,ReplyKeyboardRemove

from config import DB_NAME
from keyboards.admin_inline_keyboards import yes_or_no, make_category_list, product_edit
from states.admin_states import CategoryStates
from utils.database import Database
from keyboards.keyboard import cancel
admin_message_router = Router()
db = Database(DB_NAME)


@admin_message_router.message(CategoryStates.newCategory_state)
async def new_category_handler(message: Message, state: FSMContext):
    res = db.add_category(message.text)
    if res['status']:
        await message.answer("New category successfully added")
        await state.clear()
    elif res['desc'] == 'exists':
        await message.reply("This category already exists.\n"
                            "Please, send other name or click /cancel")
    else:
        await message.reply(res['desc'])
@admin_message_router.callback_query(CategoryStates.delCategory_state)
async def del_category(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.update_data(name=query.data)
    await query.message.answer(text="Delete Category?",reply_markup=yes_or_no)
    await state.set_state(CategoryStates.delCategory)
@admin_message_router.message(CategoryStates.delCategory_state)
async def del_error(msg:Message):
    await msg.answer("Are you kidding me?\nI said 'Choose category'.",reply_markup=make_category_list())
@admin_message_router.callback_query(CategoryStates.delCategory)
async def delcategory(query: CallbackQuery,state: FSMContext):
    if query.data == "yes":
        await query.message.delete()
        if db.del_category(str((await state.get_data()).get("name"))):
            await query.message.answer(text="Category deleted")
            await state.clear()
        else:
            await query.message.answer(text="Unknown error..")
            await state.clear()
    else:
        await query.message.delete()
        await query.answer("Canceled")
@admin_message_router.message(CategoryStates.add_product_name)
async def product_name(msg: Message, state: FSMContext):
    await state.update_data(name=msg.text)
    await msg.answer(text="Please send product photo",reply_markup=cancel)
    await state.set_state(CategoryStates.add_product_img)

@admin_message_router.message(CategoryStates.add_product_img)
async def add_img(msg: Message, state: FSMContext):
    if msg.text != "cancel":
        try:
            await state.update_data(img_url=msg.photo[-1].file_id)
            await msg.answer(text="Please send product category",reply_markup=cancel)
            await state.set_state(CategoryStates.add_product_category)
        except:
            await msg.answer(text="send me only photo")
    else:
        await state.clear()
        await msg.answer("Canceled",reply_markup=ReplyKeyboardRemove())
@admin_message_router.message(CategoryStates.add_product_category)
async def add_category(msg: Message, state: FSMContext):
    if msg.text != "cancel":
        if db.get_categorie(msg.text):
            await state.update_data(category=msg.text)
            data = await state.get_data()
            info = f"Product information:\n\n\tProduct name: {data.get('name')}\nProduct category{data.get('category')}\n\nSave information about this product?"
            await msg.answer_photo(photo=data.get("img_url"),caption=info,reply_markup=yes_or_no)
            await state.set_state(CategoryStates.add_product)
        else:
            await msg.answer(text="this category did not found")
    else:
        await state.clear()
        await msg.answer("Canceled",reply_markup=ReplyKeyboardRemove())
@admin_message_router.callback_query(CategoryStates.add_product)
async def add_product(query: CallbackQuery, state: FSMContext):
    if query.data == "yes":
        data = await state.get_data()
        if db.add_product(name=data.get("name"),img=data.get("img_url"),category_name=data.get("category")):
            await query.message.delete()
            await query.answer(text="Product saved")
            await query.message.answer("Menu")
            await state.clear()
        else:
            await query.message.delete()
            await query.answer(text="Unknown error")
            await query.message.answer("Menu")
    else:
        await query.message.delete()
        await query.answer(text="canceled")
        await query.message.answer("Menu")

@admin_message_router.callback_query(CategoryStates.edit_product)
async def edit_product(query: CallbackQuery, state: FSMContext):
    await state.update_data(product_name=query.data)
    await query.message.delete()
    await query.message.answer(text="Choose one of these",reply_markup=product_edit)
    await state.set_state(CategoryStates.edit_p)
@admin_message_router.callback_query(CategoryStates.edit_p)
async def edit_product1(query: CallbackQuery, state: FSMContext):
    if query.data == "name":
        await query.message.delete()
        await query.message.answer(text="Send me a new name")
    elif query.data == "photo":
        pass
    else:
        pass