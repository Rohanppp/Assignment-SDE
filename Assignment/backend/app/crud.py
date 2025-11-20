from collections.abc import Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models


def list_reviews(db: Session) -> Sequence[models.Review]:
    stmt = select(models.Review).order_by(models.Review.created_at.desc())
    return db.execute(stmt).scalars().all()


def get_conversation(db: Session, contact_number: str) -> models.ConversationState | None:
    stmt = select(models.ConversationState).where(models.ConversationState.contact_number == contact_number)
    return db.execute(stmt).scalar_one_or_none()


def upsert_conversation(
    db: Session, contact_number: str, stage: str, product_name: str | None = None, user_name: str | None = None
) -> models.ConversationState:
    conversation = get_conversation(db, contact_number)
    if conversation is None:
        conversation = models.ConversationState(
            contact_number=contact_number, stage=stage, product_name=product_name, user_name=user_name
        )
        db.add(conversation)
    else:
        conversation.stage = stage
        if product_name is not None:
            conversation.product_name = product_name
        if user_name is not None:
            conversation.user_name = user_name
    db.commit()
    db.refresh(conversation)
    return conversation


def delete_conversation(db: Session, contact_number: str) -> None:
    conversation = get_conversation(db, contact_number)
    if conversation:
        db.delete(conversation)
        db.commit()


def persist_review(
    db: Session, *, contact_number: str, user_name: str, product_name: str, product_review: str
) -> models.Review:
    review = models.Review(
        contact_number=contact_number,
        user_name=user_name,
        product_name=product_name,
        product_review=product_review,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review

