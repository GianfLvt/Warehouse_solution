from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://warehouse:warehouse_secret_2026@db:5432/warehouse"
    SECRET_KEY: str = "j8s2kd9f3m5n7b1v4x6z0w2q8e5r3t7y9u1i4o6p"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
