from functools import lru_cache
from os import getenv


@lru_cache(maxsize=1)
def get_settings() -> dict[str, str | None]:
    return {
        "supabase_url": getenv("SUPABASE_URL"),
        "supabase_service_role_key": getenv("SUPABASE_SERVICE_ROLE_KEY"),
        "api_prefix": getenv("API_PREFIX", "/api"),
    }
