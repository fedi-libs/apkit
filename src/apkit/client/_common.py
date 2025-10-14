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

def _is_expected_content_type(actual_ctype: str, expected_ctype_prefix: str) -> bool:    
    mime_type = actual_ctype.split(';')[0].strip().lower()

    if mime_type == 'application/json':
        return True
    if mime_type.endswith('+json'):
        return True
    
    if expected_ctype_prefix and mime_type.startswith(expected_ctype_prefix.split(';')[0].lower()):
         return True

    return False