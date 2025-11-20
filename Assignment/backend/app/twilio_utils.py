from collections.abc import Mapping

from fastapi import Request
from twilio.request_validator import RequestValidator


def is_valid_signature(request: Request, params: Mapping[str, str | None], auth_token: str) -> bool:
    """
    Validate an incoming Twilio webhook using the provided auth token.
    """
    signature = request.headers.get("X-Twilio-Signature", "")
    validator = RequestValidator(auth_token)
    # Filter out None values because Twilio only signs fields that exist in the payload
    filtered_params = {key: value for key, value in params.items() if value is not None}
    return validator.validate(str(request.url), filtered_params, signature)

