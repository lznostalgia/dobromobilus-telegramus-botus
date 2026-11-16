from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from db.database import Database
from db.repositories.shelter import (
    get_cities,
    get_shelters
)
from db.repositories.pet import (
    get_animal_types,
    get_pets,
    get_pet,
)
from db.repositories.application import create_application

from tgbot.states.user import UserStates
from tgbot.keyboards.inline import (
    main_menu_keyboard,
    animal_types_keyboard,
    cities_keyboard,
    shelters_keyboard,
    pets_keyboard,
    pet_details_keyboard,
    confirm_application_keyboard,
    BrowseCallback,
    AnimalTypeCallback,
    CityCallback,
    ShelterCallback,
    PetCallback,
    PetActionCallback,
    BackCallback,
)


router = Router(name="user")


# ---------- DISPLAY HELPERS ----------

async def show_types(
    callback: CallbackQuery,
    state: FSMContext,
    db: Database,
):
    async with db.session_factory() as session:
        animal_types = await get_animal_types(session)

    if not animal_types:
        if callback.message:
            await callback.message.edit_text(
                "Пока нет доступных животных."
            )
        await callback.answer()
        return

    await state.clear()
    await state.update_data(animal_types=animal_types)
    await state.set_state(UserStates.choosing_animal_type)

    if callback.message:
        await callback.message.edit_text(
            "Какого питомца вы ищете?",
            reply_markup=animal_types_keyboard(animal_types),
        )

    await callback.answer()


async def show_cities(
    callback: CallbackQuery,
    state: FSMContext,
    db: Database,
):
    data = await state.get_data()
    animal_type = data.get("animal_type")

    if not animal_type:
        await callback.answer(
            "Начните выбор заново.",
            show_alert=True,
        )
        return

    async with db.session_factory() as session:
        cities = await get_cities(session, animal_type)

    if not cities:
        if callback.message:
            await callback.message.edit_text(
                "В этой категории пока нет доступных городов."
            )
        await callback.answer()
        return

    await state.update_data(cities=cities)
    await state.set_state(UserStates.choosing_city)

    if callback.message:
        await callback.message.edit_text(
            "Выберите город:",
            reply_markup=cities_keyboard(cities),
        )

    await callback.answer()


async def show_shelters(
    callback: CallbackQuery,
    state: FSMContext,
    db: Database,
):
    data = await state.get_data()

    animal_type = data.get("animal_type")
    city = data.get("city")

    if not animal_type or not city:
        await callback.answer(
            "Начните выбор заново.",
            show_alert=True,
        )
        return

    async with db.session_factory() as session:
        shelters = await get_shelters(
            session,
            city,
            animal_type,
        )

    if not shelters:
        if callback.message:
            await callback.message.edit_text(
                "В этом городе нет подходящих приютов."
            )
        await callback.answer()
        return

    await state.set_state(UserStates.choosing_shelter)

    text = "Выберите приют:\n\n"

    for shelter in shelters:
        text += (
            f"**{shelter.name}**\n"
            f"Адрес: {shelter.address}\n\n"
        )

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=shelters_keyboard(shelters),
            parse_mode="Markdown",
        )

    await callback.answer()


async def show_pets(
    callback: CallbackQuery,
    state: FSMContext,
    db: Database,
):
    data = await state.get_data()

    shelter_id = data.get("shelter_id")
    animal_type = data.get("animal_type")

    if shelter_id is None or not animal_type:
        await callback.answer(
            "Начните выбор заново.",
            show_alert=True,
        )
        return

    async with db.session_factory() as session:
        pets = await get_pets(
            session,
            shelter_id,
            animal_type,
        )

    if not pets:
        if callback.message:
            await callback.message.edit_text(
                "В этом приюте пока нет доступных питомцев."
            )
        await callback.answer()
        return

    await state.set_state(UserStates.choosing_pet)

    if callback.message:
        await callback.message.edit_text(
            "Выберите питомца:",
            reply_markup=pets_keyboard(pets),
        )

    await callback.answer()


async def show_pet(
    callback: CallbackQuery,
    state: FSMContext,
    db: Database,
    pet_id: int,
):
    async with db.session_factory() as session:
        pet = await get_pet(session, pet_id)

    if pet is None or not pet.is_available:
        await callback.answer(
            "Этот питомец больше недоступен.",
            show_alert=True,
        )
        return

    await state.update_data(selected_pet_id=pet.id)
    await state.set_state(UserStates.viewing_pet)

    text = (
        f"Питомец: {pet.name}\n"
        f"Категория: {pet.animal_type}\n\n"
        f"Приют: {pet.shelter.name}\n"
        f"Город: {pet.shelter.city}\n"
        f"Адрес: {pet.shelter.address}\n"
    )

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=pet_details_keyboard(pet.id),
        )

    await callback.answer()


# ---------- USER ENTRY ----------

@router.message(CommandStart())
async def start(
    message: Message,
    state: FSMContext,
):
    await state.clear()

    await message.answer(
        "Добро пожаловать в бот приюта!\n"
        "Поможем найти питомца.",
        reply_markup=main_menu_keyboard(),
    )


@router.callback_query(BrowseCallback.filter())
async def browse(
    callback: CallbackQuery,
    state: FSMContext,
    db: Database,
):
    await show_types(callback, state, db)


# ---------- CATEGORY ----------

@router.callback_query(AnimalTypeCallback.filter())
async def choose_animal_type(
    callback: CallbackQuery,
    callback_data: AnimalTypeCallback,
    state: FSMContext,
    db: Database,
):
    data = await state.get_data()
    animal_types = data.get("animal_types", [])

    index = callback_data.index

    if not 0 <= index < len(animal_types):
        await callback.answer(
            "Список устарел. Начните сначала.",
            show_alert=True,
        )
        return

    await state.update_data(
        animal_type=animal_types[index]
    )

    await show_cities(callback, state, db)


# ---------- CITY ----------

@router.callback_query(CityCallback.filter())
async def choose_city(
    callback: CallbackQuery,
    callback_data: CityCallback,
    state: FSMContext,
    db: Database,
):
    data = await state.get_data()
    cities = data.get("cities", [])

    index = callback_data.index

    if not 0 <= index < len(cities):
        await callback.answer(
            "Список устарел. Начните сначала.",
            show_alert=True,
        )
        return

    await state.update_data(city=cities[index])

    await show_shelters(callback, state, db)


# ---------- SHELTER ----------

@router.callback_query(ShelterCallback.filter())
async def choose_shelter(
    callback: CallbackQuery,
    callback_data: ShelterCallback,
    state: FSMContext,
    db: Database,
):
    data = await state.get_data()

    city = data.get("city")
    animal_type = data.get("animal_type")

    async with db.session_factory() as session:
        shelters = await get_shelters(
            session,
            city,
            animal_type,
        )

    if not any(
        shelter.id == callback_data.shelter_id
        for shelter in shelters
    ):
        await callback.answer(
            "Этот приют больше недоступен в выбранном списке.",
            show_alert=True,
        )
        return

    await state.update_data(
        shelter_id=callback_data.shelter_id
    )

    await show_pets(callback, state, db)


# ---------- PET ----------

@router.callback_query(PetCallback.filter())
async def choose_pet(
    callback: CallbackQuery,
    callback_data: PetCallback,
    state: FSMContext,
    db: Database,
):
    data = await state.get_data()

    shelter_id = data.get("shelter_id")
    animal_type = data.get("animal_type")

    async with db.session_factory() as session:
        pets = await get_pets(
            session,
            shelter_id,
            animal_type,
        )

    if not any(
        pet.id == callback_data.pet_id
        for pet in pets
    ):
        await callback.answer(
            "Этот питомец больше недоступен.",
            show_alert=True,
        )
        return

    await show_pet(
        callback,
        state,
        db,
        callback_data.pet_id,
    )


# ---------- APPLICATION ----------

@router.callback_query(PetActionCallback.filter())
async def pet_action(
    callback: CallbackQuery,
    callback_data: PetActionCallback,
    state: FSMContext,
    db: Database,
):
    if callback_data.action == "apply":
        await state.update_data(
            selected_pet_id=callback_data.pet_id
        )
        await state.set_state(
            UserStates.confirming_application
        )

        if callback.message:
            await callback.message.edit_text(
                "Подтвердите, что хотите оставить заявку "
                "на выбранного питомца.",
                reply_markup=confirm_application_keyboard(
                    callback_data.pet_id
                ),
            )

        await callback.answer()
        return

    if callback_data.action == "confirm":
        pet_id = callback_data.pet_id

        # Проверяем, что пользователь действительно выбрал этого питомца.
        data = await state.get_data()

        if data.get("selected_pet_id") != pet_id:
            await callback.answer(
                "Выбор устарел. Начните сначала.",
                show_alert=True,
            )
            return

        user = callback.from_user

        async with db.session_factory.begin() as session:
            result = await create_application(
                session=session,
                telegram_user_id=user.id,
                telegram_username=user.username,
                pet_id=pet_id,
            )

        if result == "created":
            text = "Заявка успешно отправлена!"
        elif result == "duplicate":
            text = "Вы уже оставляли заявку на этого питомца."
        else:
            text = "К сожалению, питомец больше недоступен."

        await state.clear()

        if callback.message:
            await callback.message.edit_text(
                text,
                reply_markup=main_menu_keyboard(),
            )

        await callback.answer()
        return


# ---------- BACK NAVIGATION ----------

@router.callback_query(BackCallback.filter())
async def go_back(
    callback: CallbackQuery,
    callback_data: BackCallback,
    state: FSMContext,
    db: Database,
):
    target = callback_data.target

    if target == "types":
        await show_types(callback, state, db)

    elif target == "cities":
        await show_cities(callback, state, db)

    elif target == "shelters":
        await show_shelters(callback, state, db)

    elif target == "pets":
        await show_pets(callback, state, db)

    elif target == "pet":
        data = await state.get_data()
        pet_id = data.get("selected_pet_id")

        if pet_id is None:
            await callback.answer(
                "Начните выбор заново.",
                show_alert=True,
            )
            return

        await show_pet(callback, state, db, pet_id)

    else:
        await callback.answer(
            "Неизвестное действие.",
            show_alert=True,
        )