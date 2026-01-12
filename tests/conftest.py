import os

# Default env vars for settings to work in tests
os.environ.setdefault("DB__URL", "postgresql+asyncpg://user:pass@localhost/db")
os.environ.setdefault("REDIS__URL", "redis://localhost:6379/0")
os.environ.setdefault("RABBIT__URL", "amqp://guest:guest@localhost/")
os.environ.setdefault("RABBIT__NOTIFICATIONS_QUEUE", "notifications.send")
os.environ.setdefault("RABBIT__MAX_RETRIES", "3")
