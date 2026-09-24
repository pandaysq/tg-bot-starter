from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from app.config import Settings
from app.database.engine import Database
from app.keyboards.support import CATEGORIES, close_ticket_keyboard
from app.services.tickets import TicketService

router = Router(name="support")


class SupportForm(StatesGroup):
    waiting_for_message = State()


@router.callback_query(F.data.startswith("category:"))
async def choose_category(callback: CallbackQuery, state: FSMContext) -> None:
    category = callback.data.partition(":")[2] if callback.data else ""
    if category not in CATEGORIES:
        await callback.answer("Неизвестная категория", show_alert=True)
        return
    await state.update_data(category=category)
    await state.set_state(SupportForm.waiting_for_message)
    await callback.message.edit_text(
        f"Категория: {CATEGORIES[category]}\n\nОпишите вопрос одним сообщением."
    )
    await callback.answer()


@router.message(SupportForm.waiting_for_message, F.text)
async def receive_request(
    message: Message,
    state: FSMContext,
    bot: Bot,
    database: Database,
    settings: Settings,
) -> None:
    if message.from_user is None:
        return
    data = await state.get_data()
    category = str(data["category"])
    service = TicketService(database)
    ticket = await service.create(
        user_id=message.from_user.id,
        username=message.from_user.username,
        category=category,
        message=message.text,
    )
    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else message.from_user.full_name
    )
    admin_message = await bot.send_message(
        settings.admin_chat_id,
        (
            f"Тикет #{ticket.id}\n"
            f"От: {username} (ID {message.from_user.id})\n"
            f"Категория: {CATEGORIES[category]}\n\n"
            f"{message.text}\n\n"
            "Ответьте реплаем на это сообщение."
        ),
        reply_markup=close_ticket_keyboard(ticket.id),
    )
    await service.bind_admin_message(ticket.id, admin_message.message_id)
    await state.clear()
    await message.answer(
        f"Обращение #{ticket.id} принято. Ответ придёт в этот чат."
    )


@router.message(SupportForm.waiting_for_message)
async def require_text(message: Message) -> None:
    await message.answer("Пожалуйста, отправьте обращение текстом.")