from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """
    Manages application configuration using Pydantic, loading from a .env file.
    """
    model_config = SettingsConfigDict(
        env_file='.env', 
        env_file_encoding='utf-8', 
        extra='ignore'
    )

    spotify_client_id: str
    spotify_client_secret: str
    encryption_key: str
    redirect_uri: str = "http://127.0.0.1:9090"
    database_url: str = "sqlite:///./tempoweave.db"


settings = AppConfig()
