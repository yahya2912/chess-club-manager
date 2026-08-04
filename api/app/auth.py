from fastapi import Header, HTTPException, status


def require_api_key(x_api_key: str | None = Header(default=None)):
    """FastAPI dependency enforcing the X-API-Key header.
    Returns 401 for both missing and invalid keys.
    """
    from app import config
    if x_api_key != config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
