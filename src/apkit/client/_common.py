# This file will contain common logic shared between sync and asyncio clients.
from .models import Resource, WebfingerResult

def build_webfinger_url(host: str, resource: Resource) -> str:
    """Builds a WebFinger URL."""
    return f"https://{host}/.well-known/webfinger?resource={resource}"


def validate_webfinger_result(result: WebfingerResult, expected_subject: Resource) -> None:
    """Validates the subject in a WebfingerResult."""
    if result.subject != expected_subject:
        raise ValueError(
            f"Mismatched subject in response. Expected {expected_subject}, got {result.subject}"
        )
