from database import engine
from sqlalchemy import text


async def get_table_names(conn) -> set[str]:
    dialect = conn.dialect.name

    if dialect == "sqlite":
        result = await conn.exec_driver_sql(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        return {row[0] for row in result.fetchall()}

    if dialect == "postgresql":
        result = await conn.exec_driver_sql(
            """
            SELECT tablename
            FROM pg_catalog.pg_tables
            WHERE schemaname = 'public'
            """
        )
        return {row[0] for row in result.fetchall()}

    raise RuntimeError(f"Unsupported database dialect: {dialect}")


async def get_column_names(conn, table_name: str) -> set[str]:
    dialect = conn.dialect.name

    if dialect == "sqlite":
        result = await conn.exec_driver_sql(f"PRAGMA table_info({table_name})")
        return {row["name"] for row in result.mappings().all()}

    if dialect == "postgresql":
        result = await conn.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = :table_name
                """
            ),
            {"table_name": table_name},
        )
        return {row[0] for row in result.fetchall()}

    raise RuntimeError(f"Unsupported database dialect: {dialect}")


def column_type(conn, sqlite_type: str, postgres_type: str) -> str:
    if conn.dialect.name == "postgresql":
        return postgres_type

    return sqlite_type


def boolean_default(conn) -> str:
    if conn.dialect.name == "postgresql":
        return "FALSE"

    return "0"


async def add_column_if_missing(
    conn,
    table_name: str,
    columns: set[str],
    column_name: str,
    column_sql: str,
):
    if column_name not in columns:
        await conn.exec_driver_sql(f"ALTER TABLE {table_name} ADD COLUMN {column_sql}")
        columns.add(column_name)


async def ensure_user_schema():
    async with engine.begin() as conn:
        tables = await get_table_names(conn)

        if "users" not in tables:
            return

        columns = await get_column_names(conn, "users")

        await add_column_if_missing(
            conn,
            "users",
            columns,
            "is_admin",
            f"is_admin BOOLEAN NOT NULL DEFAULT {boolean_default(conn)}",
        )


async def ensure_message_schema():
    async with engine.begin() as conn:
        tables = await get_table_names(conn)

        if "messages" not in tables:
            return

        columns = await get_column_names(conn, "messages")

        await add_column_if_missing(
            conn,
            "messages",
            columns,
            "content_type",
            "content_type VARCHAR(20) NOT NULL DEFAULT 'text'",
        )

        await add_column_if_missing(
            conn,
            "messages",
            columns,
            "media_url",
            "media_url VARCHAR(500)",
        )

        await add_column_if_missing(
            conn,
            "messages",
            columns,
            "file_name",
            "file_name VARCHAR(255)",
        )

        await add_column_if_missing(
            conn,
            "messages",
            columns,
            "mime_type",
            "mime_type VARCHAR(255)",
        )

        await add_column_if_missing(
            conn,
            "messages",
            columns,
            "file_size",
            "file_size INTEGER",
        )

        await add_column_if_missing(
            conn,
            "messages",
            columns,
            "reply_to_id",
            "reply_to_id INTEGER",
        )

        edited_at_type = column_type(
            conn,
            sqlite_type="DATETIME",
            postgres_type="TIMESTAMP",
        )

        await add_column_if_missing(
            conn,
            "messages",
            columns,
            "edited_at",
            f"edited_at {edited_at_type}",
        )
