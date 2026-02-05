from database.models import Base
from database.session import SessionManager


async def init_db():
    session_manager = SessionManager("sqlite+aiosqlite:///./db.sqlite3")

    async with session_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
