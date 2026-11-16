from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.models import Shelter, Pet, Admin


# ---------- CALLBACK DATA ----------

class BrowseCallback(CallbackData, prefix="browse"):
    action: str


class AnimalTypeCallback(CallbackData, prefix="atype"):
    index: int


class CityCallback(CallbackData, prefix="city"):
    index: int


class ShelterCallback(CallbackData, prefix="shelter"):
    shelter_id: int


class PetCallback(CallbackData, prefix="pet"):
    pet_id: int


class PetActionCallback(CallbackData, prefix="petact"):
    action: str
    pet_id: int


class BackCallback(CallbackData, prefix="back"):
    target: str


class AdminActionCallback(CallbackData, prefix="admin"):
    action: str


class RemoveAdminCallback(CallbackData, prefix="rmadmin"):
    telegram_id: int


# ---------- USER KEYBOARDS ----------

def main_menu_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Хочу питомца",
        callback_data=BrowseCallback(action="start"),
    )

    return builder.as_markup()


def animal_types_keyboard(animal_types: list[str]):
    builder = InlineKeyboardBuilder()

    for index, animal_type in enumerate(animal_types):
        builder.button(
            text=animal_type,
            callback_data=AnimalTypeCallback(index=index),
        )

    builder.adjust(2)

    return builder.as_markup()


def cities_keyboard(cities: list[str]):
    builder = InlineKeyboardBuilder()

    for index, city in enumerate(cities):
        builder.button(
            text=city,
            callback_data=CityCallback(index=index),
        )

    builder.button(
        text="Назад",
        callback_data=BackCallback(target="types"),
    )

    builder.adjust(2)

    return builder.as_markup()


def shelters_keyboard(shelters: list[Shelter]):
    builder = InlineKeyboardBuilder()

    for shelter in shelters:
        builder.button(
            text=f"{shelter.name} — {shelter.address}",
            callback_data=ShelterCallback(
                shelter_id=shelter.id
            ),
        )

    builder.button(
        text="Назад",
        callback_data=BackCallback(target="cities"),
    )

    builder.adjust(1)

    return builder.as_markup()


def pets_keyboard(pets: list[Pet]):
    builder = InlineKeyboardBuilder()

    for pet in pets:
        builder.button(
            text=pet.name,
            callback_data=PetCallback(pet_id=pet.id),
        )

    builder.button(
        text="Назад",
        callback_data=BackCallback(target="shelters"),
    )

    builder.adjust(2)

    return builder.as_markup()


def pet_details_keyboard(pet_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Оставить заявку",
        callback_data=PetActionCallback(
            action="apply",
            pet_id=pet_id,
        ),
    )

    builder.button(
        text="Назад",
        callback_data=BackCallback(target="pets"),
    )

    builder.adjust(1)

    return builder.as_markup()


def confirm_application_keyboard(pet_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Подтвердить заявку",
        callback_data=PetActionCallback(
            action="confirm",
            pet_id=pet_id,
        ),
    )

    builder.button(
        text="Назад",
        callback_data=BackCallback(target="pet"),
    )

    builder.adjust(1)

    return builder.as_markup()


# ---------- ADMIN KEYBOARDS ----------

def admin_menu_keyboard(is_root: bool):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Заявки",
        callback_data=AdminActionCallback(
            action="applications"
        ),
    )

    if is_root:
        builder.button(
            text="Дополнительные администраторы",
            callback_data=AdminActionCallback(
                action="admins"
            ),
        )

    builder.adjust(1)

    return builder.as_markup()


def admin_ids_keyboard(admins: list[Admin]):
    builder = InlineKeyboardBuilder()

    for admin in admins:
        builder.button(
            text=f"Удалить ID {admin.telegram_id}",
            callback_data=RemoveAdminCallback(
                telegram_id=admin.telegram_id
            ),
        )

    builder.button(
        text="Добавить администратора",
        callback_data=AdminActionCallback(
            action="add_admin"
        ),
    )

    builder.button(
        text="Назад",
        callback_data=AdminActionCallback(
            action="menu"
        ),
    )

    builder.adjust(1)

    return builder.as_markup()


def cancel_add_admin_keyboard():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Отмена",
        callback_data=AdminActionCallback(
            action="cancel_add"
        ),
    )

    return builder.as_markup()