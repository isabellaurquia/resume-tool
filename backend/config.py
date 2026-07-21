from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field
import yaml


PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    openai_api_key: str = ""
    serpapi_api_key: str = ""
    database_url: str = f"sqlite:///{PROJECT_ROOT / 'jobpilot.db'}"
    scrape_interval_hours: int = 6
    score_threshold: int = 50

    model_config = {"env_file": str(PROJECT_ROOT / ".env"), "extra": "ignore"}


settings = Settings()


def load_profile() -> dict:
    profile_path = PROJECT_ROOT / "profile.yaml"
    if not profile_path.exists():
        raise FileNotFoundError(
            f"profile.yaml not found at {profile_path}. "
            "Copy profile.example.yaml and fill in your details."
        )
    with open(profile_path) as f:
        return yaml.safe_load(f)
