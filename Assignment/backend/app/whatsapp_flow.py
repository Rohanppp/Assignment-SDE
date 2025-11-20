from sqlalchemy.orm import Session

from . import crud

PROMPTS = {
    "ask_product": "Which product is this review for?",
    "ask_name": "What's your name?",
    "ask_review": "Please send your review for {product}.",
    "saved": "Thanks {user} — your review for {product} has been recorded.",
    "reset": "Let's start over. Which product is this review for?",
}


def _twiml(message: str) -> str:
    safe = message.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f"<Response><Message>{safe}</Message></Response>"


def handle_reset(db: Session, contact_number: str) -> str:
    crud.delete_conversation(db, contact_number)
    crud.upsert_conversation(db, contact_number=contact_number, stage="awaiting_product")
    return _twiml(PROMPTS["reset"])


def handle_message(db: Session, contact_number: str, incoming_text: str) -> str:
    normalized = incoming_text.strip()
    lower = normalized.lower()

    if lower in {"reset", "restart", "start"}:
        return handle_reset(db, contact_number)

    conversation = crud.get_conversation(db, contact_number)

    if conversation is None:
        crud.upsert_conversation(db, contact_number=contact_number, stage="awaiting_product")
        return _twiml(PROMPTS["ask_product"])

    if conversation.stage == "awaiting_product":
        crud.upsert_conversation(db, contact_number, stage="awaiting_user_name", product_name=normalized)
        return _twiml(PROMPTS["ask_name"])

    if conversation.stage == "awaiting_user_name":
        crud.upsert_conversation(db, contact_number, stage="awaiting_review", user_name=normalized)
        return _twiml(PROMPTS["ask_review"].format(product=conversation.product_name or "the product"))

    if conversation.stage == "awaiting_review":
        product_name = conversation.product_name or "the product"
        user_name = conversation.user_name or "there"
        crud.persist_review(
            db,
            contact_number=contact_number,
            user_name=user_name,
            product_name=product_name,
            product_review=normalized,
        )
        crud.delete_conversation(db, contact_number)
        return _twiml(PROMPTS["saved"].format(user=user_name, product=product_name))

    crud.delete_conversation(db, contact_number)
    crud.upsert_conversation(db, contact_number=contact_number, stage="awaiting_product")
    return _twiml(PROMPTS["ask_product"])

