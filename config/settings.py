import os

class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_LINK_MODEL: str = "gpt-4o-mini"
    OPENAI_CHAT_MODEL: str = "gpt-4o"

settings = Settings()
