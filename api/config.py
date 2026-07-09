from functools import lru_cache
from os import getenv


@lru_cache(maxsize=1)
def get_settings() -> dict[str, str | None]:
    return {
        "supabase_url": getenv("SUPABASE_URL"),
        "supabase_publishable_key": getenv("SUPABASE_PUBLISHABLE_KEY") or getenv("SUPABASE_ANON_KEY"),
        "supabase_secret_key": getenv("SUPABASE_SECRET_KEY") or getenv("SUPABASE_SERVICE_ROLE_KEY"),
        "supabase_jwks_url": getenv("SUPABASE_JWKS_URL"),
        "api_prefix": getenv("API_PREFIX", "/api"),
    }
