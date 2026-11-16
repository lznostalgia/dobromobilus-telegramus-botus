from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

from db.database import Database
from db.repositories.admin import (
    is_extra_admin,
    get_extra_admins,
    add_extra_admin,
    remove_extra_admin,
)
from db.repositories.application import get_applications

from config import ADMIN_IDS
from tgbot.states.admin import AdminStates
from tgbot.keyboards.inline import (
    admin_menu_keyboard,
    admin_ids_keyboard,
    cancel_add_admin_keyboard,
    AdminActionCallback,
    RemoveAdminCallback,
)


router = Router(name="admin")


# ---------- AUTHORIZATION ----------

async def is_admin_user(
    db: Database,
    telegram_id: int,
) -> bool:
    # Основные администраторы из .env
    if telegram_id in ADMIN_IDS:
        return True

    # Дополнительные администраторы из БД
    async with db.session_factory() as session:
        return await is_extra_admin(session, telegram_id)


def is_root_admin(telegram_id: int) -> bool:
    return telegram_id in ADMIN_IDS


async def reject_access(message: Message):
    await message.answer("У вас нет доступа к админ-панели.")


# ---------- ADMIN MENU ----------

@router.message(Command("admin"))
async def admin_start(
    message: Message,
    db: Database,
):
    if message.from_user is None:
        return

    if not await is_admin_user(db, message.from_user.id):
        await reject_access(message)
        return

    await message.answer(
        "Панель администратора:",
        reply_markup=admin_menu_keyboard(
            is_root=is_root_admin(message.from_user.id)
        ),
    )


# ---------- APPLICATIONS ----------

async def show_applications(
    callback: CallbackQuery,
    db: Database,
):
    async with db.session_factory() as session:
        applications = await get_applications(
            session,
            limit=10,
        )

    if not applications:
        text = "Заявок пока нет."
    else:
        lines = ["Последние заявки:\n"]

        for application in applications:
            pet = application.pet

            created_at = (
                application.created_at.strftime("%d.%m.%Y %H:%M")
                if application.created_at
                else "неизвестно"
            )

            username = (
                f"@{application.telegram_username}"
                if application.telegram_username
                else "не указан"
            )

            if pet:
                shelter_name = pet.shelter.name if pet.shelter else "неизвестен"
                pet_info = f"{pet.name} ({pet.animal_type})"
            else:
                shelter_name = "неизвестен"
                pet_info = "питомец не найден"

            lines.append(
                f"Заявка #{application.id}\n"
                f"Пользователь ID: {application.telegram_user_id}\n"
                f"Username: {username}\n"
                f"Питомец: {pet_info}\n"
                f"Приют: {shelter_name}\n"
                f"Дата: {created_at}\n"
            )

        text = "\n".join(lines)

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=admin_menu_keyboard(
                is_root=is_root_admin(callback.from_user.id)
            ),
        )

    await callback.answer()


# ---------- ADDITIONAL ADMINS LIST ----------

async def show_admins(
    callback: CallbackQuery,
    db: Database,
):
    async with db.session_factory() as session:
        admins = await get_extra_admins(session)

    if admins:
        text = "Дополнительные администраторы:"
    else:
        text = "Дополнительных администраторов пока нет."

    if callback.message:
        await callback.message.edit_text(
            text,
            reply_markup=admin_ids_keyboard(admins),
        )

    await callback.answer()


# ---------- CALLBACK HANDLER ----------

@router.callback_query(AdminActionCallback.filter())
async def admin_action(
    callback: CallbackQuery,
    callback_data: AdminActionCallback,
    state: FSMContext,
    db: Database,
):
    user_id = callback.from_user.id

    # Проверяем права при каждом административном действии.
    if not await is_admin_user(db, user_id):
        await callback.answer(
            "Доступ запрещён.",
            show_alert=True,
        )
        return

    action = callback_data.action

    if action == "applications":
        await show_applications(callback, db)
        return

    if action == "menu":
        await state.clear()

        if callback.message:
            await callback.message.edit_text(
                "Панель администратора:",
                reply_markup=admin_menu_keyboard(
                    is_root=is_root_admin(user_id)
                ),
            )

        await callback.answer()
        return

    # Управлять дополнительными администраторами
    # может только основной администратор из .env.
    if action in {"admins", "add_admin", "cancel_add"}:
        if not is_root_admin(user_id):
            await callback.answer(
                "У вас нет прав управлять администраторами.",
                show_alert=True,
            )
            return

    if action == "admins":
        await show_admins(callback, db)
        return

    if action == "add_admin":
        await state.set_state(
            AdminStates.waiting_for_admin_id
        )

        if callback.message:
            await callback.message.edit_text(
                "Отправьте Telegram ID нового администратора.\n"
                "Например: 123456789",
                reply_markup=cancel_add_admin_keyboard(),
            )

        await callback.answer()
        return

    if action == "cancel_add":
        await state.clear()

        if callback.message:
            await callback.message.edit_text(
                "Добавление отменено.",
                reply_markup=admin_menu_keyboard(
                    is_root=True
                ),
            )

        await callback.answer()
        return

    await callback.answer(
        "Неизвестное действие.",
        show_alert=True,
    )


# ---------- ADD ADMIN BY MESSAGE ----------

@router.message(AdminStates.waiting_for_admin_id)
async def process_new_admin(
    message: Message,
    state: FSMContext,
    db: Database,
):
    if message.from_user is None:
        return

    user_id = message.from_user.id

    # Повторно проверяем права даже при вводе обычного сообщения.
    if not is_root_admin(user_id):
        await state.clear()
        await message.answer("Недостаточно прав.")
        return

    if not message.text:
        await message.answer(
            "Отправьте числовой Telegram ID."
        )
        return

    try:
        new_admin_id = int(message.text.strip())
    except ValueError:
        await message.answer(
            "ID должен состоять из цифр. Попробуйте ещё раз."
        )
        return

    if new_admin_id <= 0:
        await message.answer("Некорректный Telegram ID.")
        return

    if new_admin_id in ADMIN_IDS:
        await message.answer(
            "Этот пользователь уже является основным администратором."
        )
        return

    try:
        async with db.session_factory.begin() as session:
            added = await add_extra_admin(
                session,
                new_admin_id,
            )
    except IntegrityError:
        # Например, если две операции добавили один ID одновременно.
        added = False

    if added:
        result_text = (
            f"Дополнительный администратор {new_admin_id} добавлен."
        )
    else:
        result_text = (
            f"ID {new_admin_id} уже зарегистрирован как администратор."
        )

    await state.clear()

    async with db.session_factory() as session:
        admins = await get_extra_admins(session)

    await message.answer(
        result_text + "\n\nДополнительные администраторы:",
        reply_markup=admin_ids_keyboard(admins),
    )


# ---------- REMOVE ADMIN ----------

@router.callback_query(RemoveAdminCallback.filter())
async def delete_admin(
    callback: CallbackQuery,
    callback_data: RemoveAdminCallback,
    db: Database,
):
    user_id = callback.from_user.id

    # Только основные администраторы могут удалять ID.
    if not is_root_admin(user_id):
        await callback.answer(
            "Недостаточно прав.",
            show_alert=True,
        )
        return

    telegram_id = callback_data.telegram_id

    # Защита основных администраторов.
    if telegram_id in ADMIN_IDS:
        await callback.answer(
            "Нельзя удалить основного администратора.",
            show_alert=True,
        )
        return

    async with db.session_factory.begin() as session:
        removed = await remove_extra_admin(
            session,
            telegram_id,
        )

    async with db.session_factory() as session:
        admins = await get_extra_admins(session)

    text = (
        f"Администратор {telegram_id} удалён."
        if removed
        else "Администратор не найден."
    )

    if callback.message:
        await callback.message.edit_text(
            text + "\n\nДополнительные администраторы:",
            reply_markup=admin_ids_keyboard(admins),
        )

    await callback.answer()