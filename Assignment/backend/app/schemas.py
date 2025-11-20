from datetime import datetime
from pydantic import BaseModel


class ReviewOut(BaseModel):
    id: int
    contact_number: str
    user_name: str
    product_name: str
    product_review: str
    created_at: datetime

    class Config:
        from_attributes = True

