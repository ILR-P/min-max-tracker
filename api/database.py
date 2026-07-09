from functools import lru_cache

from supabase import Client, create_client

from .config import get_settings


@lru_cache(maxsize=1)
def get_supabase_client() -> Client | None:
    settings = get_settings()
    supabase_url = settings["supabase_url"]
    service_role_key = settings["supabase_secret_key"]

    if not supabase_url or not service_role_key:
        return None

    return create_client(supabase_url, service_role_key)

