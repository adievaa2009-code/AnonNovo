import logging
import os
from collections import defaultdict, deque

from openai import APIConnectionError, APIStatusError, APITimeoutError, AsyncOpenAI, OpenAIError


logger = logging.getLogger(__name__)

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = "google/gemini-2.0-flash-exp:free"
MAX_CONTEXT_MESSAGES = 8
MAX_CONTEXT_CHARS = 4000

dialog_contexts: dict[tuple[int, int], deque[tuple[int, str]]] = defaultdict(
    lambda: deque(maxlen=MAX_CONTEXT_MESSAGES)
)


def env_value(name: str) -> str:
    value = os.getenv(name)
    if value:
        return value

    try:
        with open(".env", encoding="utf-8") as env_file:
            for line in env_file:
                key, separator, raw_value = line.strip().partition("=")
                if separator and key == name:
                    return raw_value.strip().strip("'\"")
    except OSError:
        return ""

    return ""


def openrouter_api_key() -> str:
    for name in ("OPENROUTER_API_KEY", "API_OPENROUTER", "API_TOKEN"):
        value = env_value(name)
        if value and value != "...":
            return value.removeprefix("Bearer ").strip()

    return ""


def context_key(first_chat_id: int, second_chat_id: int) -> tuple[int, int]:
    return tuple(sorted((first_chat_id, second_chat_id)))


def add_dialog_message(sender_id: int, recipient_id: int, text: str | None) -> None:
    if not text:
        return

    dialog_contexts[context_key(sender_id, recipient_id)].append((sender_id, text.strip()))


def clear_dialog_context(first_chat_id: int, second_chat_id: int) -> None:
    dialog_contexts.pop(context_key(first_chat_id, second_chat_id), None)


def build_context(sender_id: int, recipient_id: int, current_text: str) -> str:
    messages = list(dialog_contexts[context_key(sender_id, recipient_id)])
    messages.append((sender_id, current_text))

    lines = []
    for message_sender_id, text in messages:
        author = "CURRENT_USER" if message_sender_id == sender_id else "INTERLOCUTOR"
        lines.append(f"{author}: {text}")

    context = "\n".join(lines)
    return context[-MAX_CONTEXT_CHARS:]


def is_token_limit_error(status: int, payload: dict | str) -> bool:
    if status == 413:
        return True

    text = str(payload).casefold()
    token_markers = (
        "token",
        "context length",
        "maximum context",
        "too many tokens",
        "input is too long",
        "prompt is too long",
    )
    return status in {400, 422} and any(marker in text for marker in token_markers)


def openrouter_client(api_key: str) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=api_key,
        base_url=OPENROUTER_BASE_URL,
        timeout=12,
        default_headers={
            "Authorization": f"Bearer {api_key}",
        },
    )


async def is_contact_or_meeting_context(
    sender_id: int,
    recipient_id: int,
    current_text: str | None,
) -> bool:
    if not current_text:
        return False

    api_key = openrouter_api_key()
    if not api_key:
        logger.warning("OpenRouter check skipped: API key is not configured")
        return False

    model = env_value("OPENROUTER_MODEL") or DEFAULT_MODEL
    context = build_context(sender_id, recipient_id, current_text)
    messages = [
        {
            "role": "system",
            "content": (
                "You are a strict safety classifier for an anonymous chat bot. "
                "Detect whether the conversation contains a suggestion, attempt, "
                "agreement, or active exchange related to an offline personal meeting "
                "or exchanging personal contacts. Contacts include phone numbers, "
                "Telegram usernames, social media, messengers, email, addresses, "
                "links to profiles, or requests to move the conversation elsewhere. "
                "Answer only YES or NO."
            ),
        },
        {
            "role": "user",
            "content": (
                "Does this context include a personal meeting proposal/contact exchange "
                "or is such an exchange already happening?\n\n"
                f"{context}"
            ),
        },
    ]

    try:
        client = openrouter_client(api_key)
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0,
            max_tokens=16,
        )

        answer = response.choices[0].message.content.strip().casefold()
        return answer.startswith("yes")
    except APIStatusError as error:
        if is_token_limit_error(error.status_code, error.response.text):
            logger.warning(
                "OpenRouter contact check skipped because of token limit: status=%s response=%s",
                error.status_code,
                error.response.text,
            )
            return False

        logger.warning(
            "OpenRouter contact check failed: status=%s response=%s",
            error.status_code,
            error.response.text,
        )
        return False
    except (APIConnectionError, APITimeoutError, OpenAIError):
        logger.exception("OpenRouter contact check failed unexpectedly")
        return False
