from uuid import uuid4


def generate_id(prefix: str) -> str:
    """Generate a backend-owned stable string id."""

    return f"{prefix}_{uuid4().hex}"
