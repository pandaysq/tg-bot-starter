from aiogram import Bot, F, Router
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.config import Settings
from app.database.engine import Database
from app.database.models import TicketStatus
from app.services.tickets import TicketService

router = Router(name="admin")


async def is_admin(bot: Bot, chat_id: int, user_id: int, settings: Settings) -> bool:
    if chat_id != settings.admin_chat_id:
        return False
    membership = await bot.get_chat_member(chat_id, user_id)
    return membership.status in {
        ChatMemberStatus.CREATOR,
        ChatMemberStatus.ADMINISTRATOR,
    }


@router.message(Command("stats"))
async def stats(message: Message, bot: Bot, database: Database, settings: Settings) -> None:
    if message.from_user is None or not await is_admin(
        bot, message.chat.id, message.from_user.id, settings
    ):
        return
    values = await TicketService(database).stats()
    await message.answer(
        "Статистика поддержки\n"
        f"За 24 часа: {values['day']}\n"
        f"За 7 дней: {values['week']}\n"
        f"Открытых: {values['open']}"
    )


@router.message(F.reply_to_message, F.text)
async def reply_to_ticket(
    message: Message,
    bot: Bot,
    database: Database,
    settings: Settings,
) -> None:
    if message.from_user is None or not await is_admin(
        bot, message.chat.id, message.from_user.id, settings
    ):
        return
    replied = message.reply_to_message
    if replied is None:
        return
    service = TicketService(database)
    ticket = await service.find_by_admin_message(replied.message_id)
    if ticket is None:
        return
    if ticket.status == TicketStatus.CLOSED:
        await message.reply("Этот тикет уже закрыт.")
        return
    await bot.send_message(
        ticket.user_id,
        f"Ответ поддержки по обращению #{ticket.id}:\n\n{message.text}",
    )
    await service.answer(ticket.id, message.from_user.id, message.text)
    await message.reply(f"Ответ по тикету #{ticket.id} отправлен клиенту.")


@router.callback_query(F.data.startswith("close:"))
async def close_ticket(
    callback: CallbackQuery,
    bot: Bot,
    database: Database,
    settings: Settings,
) -> None:
    if callback.message is None or not await is_admin(
        bot, callback.message.chat.id, callback.from_user.id, settings
    ):
        await callback.answer("Недостаточно прав", show_alert=True)
        return
    try:
        ticket_id = int(callback.data.partition(":")[2]) if callback.data else 0
    except ValueError:
        await callback.answer("Некорректный тикет", show_alert=True)
        return
    service = TicketService(database)
    ticket = await service.find_by_admin_message(callback.message.message_id)
    if ticket is None or ticket.id != ticket_id:
        await callback.answer("Тикет не найден", show_alert=True)
        return
    if ticket.status == TicketStatus.CLOSED:
        await callback.answer("Тикет уже закрыт", show_alert=True)
        return
    if not await service.close(ticket_id):
        await callback.answer("Тикет не найден", show_alert=True)
        return
    await bot.send_message(ticket.user_id, f"Обращение #{ticket.id} закрыто.")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer("Тикет закрыт")