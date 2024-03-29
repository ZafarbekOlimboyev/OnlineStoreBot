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
        await state.clear()
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
        await query.message.answer(text="Send me a new name",reply_markup=cancel)
        await state.set_state(CategoryStates.edit_name)
    elif query.data == "photo":
        await query.message.delete()
        await query.message.answer(text="Send me a new photo",reply_markup=cancel)
        await state.set_state(CategoryStates.edit_photo)
    else:
        await query.message.delete()
        await query.message.answer(text="Send me a new category",reply_markup=cancel)
        await state.set_state(CategoryStates.edit_url)
@admin_message_router.message(CategoryStates.edit_name)
async def edit_name(msg: Message, state: FSMContext):
    if db.edit_product_name(product_name=msg.text,old_product_name=(await state.get_data()).get("product_name")):
        await state.clear()
        await msg.answer("Name changed",reply_markup=ReplyKeyboardRemove())
@admin_message_router.message(CategoryStates.edit_photo)
async def edit_name(msg: Message, state: FSMContext):
    try:
        if db.edit_product_photo(photo_file_id=msg.photo[-1].file_id,product_name=(await state.get_data()).get("product_name")):
            await state.clear()
            await msg.answer("Photo changed",reply_markup=ReplyKeyboardRemove())
        else:
            await state.clear()
            await msg.answer("Unknown error", reply_markup=ReplyKeyboardRemove())
    except:
        await msg.answer(text="Send me a new photo")
@admin_message_router.message(CategoryStates.edit_url)
async def edit_category(msg: Message, state: FSMContext):
    if db.get_categorie(msg.text):
        db.edit_product_category(new_category=msg.text,product_name=(await state.get_data()).get("product_name"))
        await state.clear()
        await msg.answer(text="Category changed")
    else:
        await msg.answer(text="this category didn't found. Please send me a new category name")
@admin_message_router.callback_query(CategoryStates.del_product)
async def del_product(query: CallbackQuery, state: FSMContext):
    await query.message.delete()
    await state.update_data(name=query.data)
    await query.message.answer(text="Delete Product?", reply_markup=yes_or_no)
    await state.set_state(CategoryStates.del_product_state)
@admin_message_router.callback_query(CategoryStates.del_product_state)
async def delproduct(query: CallbackQuery, state: FSMContext):
    if query.data == "yes":
        await query.message.delete()
        if db.del_product(str((await state.get_data()).get("name"))):
            await query.message.answer(text="Product deleted")
            await state.clear()
        else:
            await query.message.answer(text="Unknown error..")
            await state.clear()
    else:
        await query.message.delete()
        await state.clear()
        await query.answer("Canceled")