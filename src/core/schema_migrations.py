from database import Base, engine


async def ensure_user_schema():
    async with engine.begin() as conn:
        result = await conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = {row[0] for row in result.fetchall()}

        if "users" not in tables:
            return

        result = await conn.exec_driver_sql("PRAGMA table_info(users)")
        columns = {row["name"] for row in result.mappings().all()}

        if "is_admin" not in columns:
            await conn.exec_driver_sql(
                "ALTER TABLE users ADD COLUMN is_admin BOOLEAN NOT NULL DEFAULT 0"
            )


async def ensure_message_schema():
    async with engine.begin() as conn:
        result = await conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = {row[0] for row in result.fetchall()}

        if "messages" not in tables:
            return

        result = await conn.exec_driver_sql("PRAGMA table_info(messages)")
        columns = {row["name"] for row in result.mappings().all()}

        if "content_type" not in columns:
            await conn.exec_driver_sql(
                "ALTER TABLE messages ADD COLUMN content_type VARCHAR(20) NOT NULL DEFAULT 'text'"
            )

        if "media_url" not in columns:
            await conn.exec_driver_sql(
                "ALTER TABLE messages ADD COLUMN media_url VARCHAR(500)"
            )

        if "file_name" not in columns:
            await conn.exec_driver_sql(
                "ALTER TABLE messages ADD COLUMN file_name VARCHAR(255)"
            )

        if "mime_type" not in columns:
            await conn.exec_driver_sql(
                "ALTER TABLE messages ADD COLUMN mime_type VARCHAR(255)"
            )

        if "file_size" not in columns:
            await conn.exec_driver_sql(
                "ALTER TABLE messages ADD COLUMN file_size INTEGER"
            )