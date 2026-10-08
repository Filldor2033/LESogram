import json
import sqlite3
from pathlib import Path

db_path = Path("chat.db").resolve()

print(f"\nDatabase: {db_path}")

if not db_path.is_file():
    raise SystemExit("Database not found!")

db = sqlite3.connect(str(db_path))

print("\n=== RECENT MESSAGES ===")

rows = db.execute("""
    SELECT id, username, room, text
    FROM messages
    ORDER BY id DESC
    LIMIT 10
""").fetchall()

for mid, user, room, text in rows:
    print(
        f"id={mid} user={user} "
        f"room={room} text={text!r}"
    )

print("\n=== BOT PERMISSIONS ===")

rows = db.execute("""
    SELECT
        b.id,
        u.username,
        r.name,
        a.can_read_messages,
        a.can_send_messages,
        b.is_active
    FROM bot_room_access a
    JOIN bots b ON b.id = a.bot_id
    JOIN users u ON u.id = b.user_id
    JOIN rooms r ON r.id = a.room_id
""").fetchall()

for row in rows:
    print(
        f"bot_id={row[0]} user={row[1]} "
        f"room={row[2]} "
        f"read={row[3]} send={row[4]} "
        f"active={row[5]}"
    )

print("\n=== BOT UPDATES ===")

rows = db.execute("""
    SELECT id, bot_id, room_id, payload
    FROM bot_updates
    ORDER BY id DESC
    LIMIT 15
""").fetchall()

for uid, bot_id, room_id, payload in rows:
    event = json.loads(payload)
    message = event.get("message", {})

    print(
        f"update_id={uid} "
        f"bot_id={bot_id} "
        f"room_id={room_id} "
        f"text={message.get('text')!r}"
    )

db.close()
