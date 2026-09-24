from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


CATEGORIES = {
    "technical": "Технический вопрос",
    "billing": "Оплата",
    "other": "Другое",
}


def category_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=label, callback_data=f"category:{key}")]
            for key, label in CATEGORIES.items()
        ]
    )


def close_ticket_keyboard(ticket_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Закрыть тикет",
                    callback_data=f"close:{ticket_id}",
                )
            ]
        ]
    )