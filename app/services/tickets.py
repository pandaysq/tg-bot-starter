from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select

from app.database.engine import Database
from app.database.models import Ticket, TicketReply, TicketStatus


class TicketService:
    def __init__(self, database: Database) -> None:
        self.database = database

    async def create(
        self, user_id: int, username: str | None, category: str, message: str
    ) -> Ticket:
        async with self.database.session_factory() as session:
            ticket = Ticket(
                user_id=user_id,
                username=username,
                category=category,
                message=message,
            )
            session.add(ticket)
            await session.commit()
            await session.refresh(ticket)
            return ticket

    async def bind_admin_message(self, ticket_id: int, message_id: int) -> None:
        async with self.database.session_factory() as session:
            ticket = await session.get(Ticket, ticket_id)
            if ticket is None:
                raise LookupError(f"Ticket {ticket_id} not found")
            ticket.admin_message_id = message_id
            await session.commit()

    async def find_by_admin_message(self, message_id: int) -> Ticket | None:
        async with self.database.session_factory() as session:
            result = await session.execute(
                select(Ticket).where(Ticket.admin_message_id == message_id)
            )
            return result.scalar_one_or_none()

    async def answer(self, ticket_id: int, admin_id: int, message: str) -> None:
        async with self.database.session_factory() as session:
            ticket = await session.get(Ticket, ticket_id)
            if ticket is None:
                raise LookupError(f"Ticket {ticket_id} not found")
            ticket.status = TicketStatus.ANSWERED
            session.add(
                TicketReply(ticket_id=ticket_id, admin_id=admin_id, message=message)
            )
            await session.commit()

    async def close(self, ticket_id: int) -> bool:
        async with self.database.session_factory() as session:
            ticket = await session.get(Ticket, ticket_id)
            if ticket is None:
                return False
            ticket.status = TicketStatus.CLOSED
            await session.commit()
            return True

    async def stats(self) -> dict[str, int]:
        now = datetime.now(UTC)
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)
        async with self.database.session_factory() as session:
            day_count = await session.scalar(
                select(func.count()).select_from(Ticket).where(Ticket.created_at >= day_ago)
            )
            week_count = await session.scalar(
                select(func.count()).select_from(Ticket).where(Ticket.created_at >= week_ago)
            )
            open_count = await session.scalar(
                select(func.count())
                .select_from(Ticket)
                .where(Ticket.status == TicketStatus.OPEN)
            )
        return {
            "day": int(day_count or 0),
            "week": int(week_count or 0),
            "open": int(open_count or 0),
        }