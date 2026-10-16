async def read_form_bytes(value) -> bytes | None:
    """Read Starlette form field as bytes (UploadFile or plain str)."""
    if value is None:
        return None
    if hasattr(value, "read"):
        return await value.read()
    return str(value).encode("utf-8")


async def read_form_field(value) -> str | None:
    """Read Starlette form field (UploadFile or plain str)."""
    if value is None:
        return None
    if hasattr(value, "read"):
        raw = await value.read()
        return raw.decode("utf-8").strip()
    return str(value).strip()
