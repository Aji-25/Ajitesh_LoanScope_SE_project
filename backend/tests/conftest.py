import os

os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://loanscope_test:loanscope_test@localhost:5432/loanscope_test",
)
os.environ.setdefault("JWT_SECRET", "test_only_secret_that_is_long_enough_for_hs256")
