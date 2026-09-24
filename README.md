# TG Bot Starter

Переиспользуемый шаблон Telegram-бота поддержки на **aiogram 3.x**. Клиент выбирает категорию, отправляет вопрос, а администратор отвечает обычным реплаем в приватной группе или канале обсуждений.

## Возможности

- асинхронный aiogram 3;
- FSM-диалог выбора категории и ввода обращения;
- пересылка тикета в административный чат;
- ответ клиенту через reply администратора;
- статусы `open`, `answered`, `closed`;
- SQLite через SQLAlchemy Async;
- `/stats` — тикеты за 24 часа, 7 дней и число открытых;
- кнопка закрытия тикета;
- Dockerfile и конфигурация через `.env`.

## Быстрый запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app
```

В `.env` укажите:

```env
BOT_TOKEN=токен_от_BotFather
ADMIN_CHAT_ID=-1001234567890
DATABASE_URL=sqlite+aiosqlite:///support_bot.db
```

Добавьте бота в административную группу. Если используется канал, подключите к нему группу обсуждений и укажите ID группы. Бот должен иметь право отправлять сообщения и получать статус участников через `getChatMember` (обычно для этого бота делают администратором группы). Отвечать на тикеты, закрывать их и смотреть `/stats` могут только администраторы этой группы.

## Docker

```bash
docker build -t tg-bot-starter .
docker run --rm --env-file .env -v "$(pwd)/data:/app/data" \
  -e DATABASE_URL=sqlite+aiosqlite:///data/support_bot.db tg-bot-starter
```

## Как устроен проект

```text
app/
├── handlers/    # Пользовательские и административные сценарии
├── keyboards/   # Inline-клавиатуры
├── services/    # Бизнес-логика тикетов
├── database/    # SQLAlchemy-модели и async engine
├── config.py    # Проверенная конфигурация из окружения
└── __main__.py  # Точка запуска и сборка приложения
```

Чтобы адаптировать шаблон:

1. Измените `CATEGORIES` в `app/keyboards/support.py`.
2. Добавьте нужную бизнес-логику в `services/`, не смешивая её с обработчиками Telegram.
3. Расширьте модели SQLAlchemy и добавьте миграции Alembic, если схема будет развиваться.
4. Подключите PostgreSQL, заменив `DATABASE_URL` и установив async-драйвер.

## Systemd

После установки зависимостей и создания `.env` можно запустить процесс как сервис:

```ini
[Unit]
Description=Telegram Support Bot
After=network-online.target

[Service]
WorkingDirectory=/opt/tg-bot-starter
EnvironmentFile=/opt/tg-bot-starter/.env
ExecStart=/opt/tg-bot-starter/.venv/bin/python -m app
Restart=on-failure
User=tgbot

[Install]
WantedBy=multi-user.target
```

## Безопасность

Токен не хранится в коде и не должен попадать в Git. Административные команды и ответы принимаются только из `ADMIN_CHAT_ID` и только от администраторов группы. Если бот не может проверить статус участника через Telegram API, команда не выполнится.