import getpass
import os
import time

import requests


API_URL = os.getenv(
    "LESOGRAM_BOT_API_URL",
    "http://127.0.0.1:8000/api/bot",
).rstrip("/")

TOKEN = os.getenv("LESOGRAM_BOT_TOKEN")

if not TOKEN:
    TOKEN = getpass.getpass("Bot API token: ")

if not TOKEN.startswith("lsg_"):
    raise SystemExit("Invalid bot token format")

session = requests.Session()
session.headers.update({
    "Authorization": f"Bot {TOKEN}",
    "Accept": "application/json",
})

def api_call(method, data=None, http_method="POST"):
    """Call a LESogram Bot API method."""

    response = session.request(
        http_method,
        f"{API_URL}/{method}",
        json=data,
        timeout=(5, 40 if method == "getUpdates" else 15),
    )

    response.raise_for_status()

    result = response.json()

    if not result.get("ok"):
        raise RuntimeError(f"Bot API error: {method}")

    return result["result"]


def send_message(chat_id, text, reply_to_id=None):
    payload = {
        "chat_id": chat_id,
        "text": text,
    }

    if reply_to_id is not None:
        payload["reply_to_id"] = reply_to_id

    return api_call("sendMessage", payload)


def handle_update(update):
    """Handle a single incoming update."""

    message = update.get("message")

    if not isinstance(message, dict):
        return

    sender = message.get("from") or {}

    # Ignore all messages from bots
    if sender.get("is_bot"):
        return

    text = message.get("text")

    if not isinstance(text, str):
        return

    chat_id = (message.get("chat") or {}).get("id")
    message_id = message.get("message_id")

    if not isinstance(chat_id, int):
        return

    text = text.strip()
    command, _, args = text.partition(" ")

    if command == "/start":
        answer = (
            "Привет! Я EchoBot\n\n"
            "Мои команды:\n"
            "/start - помощь\n"
            "/ping - проверка связи\n"
            "/echo <текст> - повторить текст"
        )

    elif command == "/ping":
        answer = "Pong!"

    elif command == "/echo":
        answer = args.strip() or (
            "Использование: /echo Привет!"
        )

    else:
        return

    print(
        f"[SEND] chat={chat_id} "
        f"reply_to={message_id} "
        f"text={answer!r}",
        flush=True,
    )

    send_message(
        chat_id,
        answer,
        reply_to_id=message_id,
    )

    print("[SEND OK]", flush=True)

    print(
        f"[{chat_id}] "
        f"{sender.get('username', 'unknown')}: "
        f"{command}"
    )


def main():
    profile = api_call(
        "getMe",
        http_method="GET",
    )

    print(f"Bot @{profile['username']} started!")
    print(f"API: {API_URL}")
    print("Waiting for messages... Ctrl+C to stop.")

    offset = 0

    while True:
        try:
            updates = api_call(
                "getUpdates",
                {
                    "offset": offset,
                    "limit": 100,
                    "timeout": 30,
                },
            )

            for update in updates:
                update_id = update["update_id"]

                message = update.get("message") or {}

                print(
                    f"[UPDATE] id={update_id} "
                    f"text={message.get('text')!r}",
                    flush=True,
                )

                if update_id < offset:
                    continue

                handle_update(update)

                # Confirm only processed updates.
                offset = update_id + 1

        except requests.HTTPError as exc:
            status = exc.response.status_code

            print(
                f"[HTTP ERROR] status={status} "
                f"body={exc.response.text[:500]}",
                flush=True,
            )

            if status in (401, 403):
                print(
                    "Check bot token and room permissions."
                )
                break

            if status == 429:
                retry = exc.response.headers.get(
                    "Retry-After", "5"
                )
                try:
                    delay = max(1, min(int(retry), 60))
                except ValueError:
                    delay = 5

                time.sleep(delay)
                continue

            time.sleep(3)

        except (
            requests.RequestException,
            ValueError,
            KeyError,
            RuntimeError,
        ) as exc:
            print(f"Temporary error: {exc}")
            time.sleep(3)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot stopped.")
    finally:
        session.close()
