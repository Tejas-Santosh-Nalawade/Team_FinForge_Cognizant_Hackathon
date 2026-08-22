import os
from urllib.parse import urlsplit, urlunsplit

from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()


def normalize_supabase_url(raw_url: str | None) -> str:
    if not raw_url:
        raise RuntimeError("SUPABASE_URL is not configured")

    normalized = raw_url.strip().rstrip("/")
    path = urlsplit(normalized).path.rstrip("/")

    for suffix in (
        "/rest/v1",
        "/auth/v1",
        "/storage/v1",
        "/realtime/v1",
        "/functions/v1",
    ):
        if path.endswith(suffix):
            path = path[: -len(suffix)]
            break

    base = urlsplit(normalized)
    normalized_url = urlunsplit((
        base.scheme,
        base.netloc,
        path,
        "",
        "",
    ))

    if not normalized_url.startswith(("http://", "https://")):
        raise RuntimeError("SUPABASE_URL must be a valid Supabase project URL")

    return normalized_url


SUPABASE_URL = normalize_supabase_url(os.getenv("SUPABASE_URL"))
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is not configured")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_SERVICE_ROLE_KEY,
)

STORAGE_BUCKET = os.getenv(
    "SUPABASE_STORAGE_BUCKET",
    "financial-files"
)