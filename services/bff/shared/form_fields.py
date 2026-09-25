async def read_form_field(value) -> str | None:
    """Read Starlette form field (UploadFile or plain str)."""
    if value is None:
        return None
    if hasattr(value, "read"):
        raw = await value.read()
        return raw.decode("utf-8").strip()
    return str(value).strip()
