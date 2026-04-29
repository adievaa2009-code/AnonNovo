# Telegram-бот на aiogram 3 (анонимные чаты)

Бот умеет находить собеседника по выбранной цели общения, пересылать сообщения между пользователями и распознавать голосовые/аудио/видео‑заметки (Vosk).

```text
├── README.md
├── main.py
├── requirements.txt
├── .env.example
├── db.sqlite3
├── downloads/
├── systemd/
│   └── bot.service
├── bot/
│   ├── config.py
│   ├── buttons/
│   │   ├── inline.py
│   │   └── keyboard.py
│   ├── handlers/
│   │   ├── callback.py
│   │   ├── commands.py
│   │   └── menu.py
│   ├── message_text/
│   │   └── text.py
│   └── misc/
│       ├── ai.py
│       ├── states.py
│       └── vosk-model-small-ru-0.22/
└── database/
    ├── initdb.py
    ├── manager.py
    ├── models.py
    ├── queries/
    │   └── users.py
    └── session.py
```

## Запуск

1. **Подготовьте окружение**

   ```
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Настройте переменные среды**

   Скопируйте пример и заполните:

   ```
   cp .env.example .env
   ```

   | Переменная  | Описание |
   |------------|----------|
   | BOT_TOKEN  | Токен Telegram‑бота |
   | ADMINS     | ID админов, через запятую |
   | API_TOKEN  | Токен для внешнего API (используется в `bot/config.py`) |
   | TEAM_ID    | Идентификатор команды для внешнего API |
   | OPENROUTER_API_KEY | Токен OpenRouter для проверки обмена контактами и личных встреч |
   | API_OPENROUTER | Альтернативное имя переменной для токена OpenRouter |
   | OPENROUTER_MODEL | Модель OpenRouter для классификации сообщений |
   | SAFETY_STOP_WORDS | Запрещенные слова, через запятую |
   | SAFETY_STOP_PHRASES | Запрещенные фразы, через запятую |

3. **Проверьте зависимости системы**

   Для обработки видео‑заметок используется `ffmpeg`. Убедитесь, что он установлен и доступен в `PATH`.

4. **Запустите бота**

   ```
   python main.py
   ```

## Примечания

- База данных SQLite создается автоматически в `db.sqlite3` при первом запуске.
- Временные файлы для распознавания аудио сохраняются в `downloads/` и удаляются после обработки.
