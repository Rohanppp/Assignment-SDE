from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sqlalchemy.orm import Session

from . import crud, schemas, whatsapp_flow, twilio_utils
from .config import get_settings
from .database import get_db, init_db


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def startup() -> None:
        init_db()

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/reviews", response_model=list[schemas.ReviewOut], tags=["reviews"])
    def list_reviews(db: Session = Depends(get_db)) -> list[schemas.ReviewOut]:
        try:
            reviews = crud.list_reviews(db)
            return [schemas.ReviewOut.model_validate(r) for r in reviews]
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching reviews: {str(e)}"
            )

    @app.post("/webhook/whatsapp", tags=["webhooks"])
    async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)) -> Response:
        form = await request.form()
        form_dict = {key: form.get(key) for key in form.keys()}

        if settings.twilio_verify_signatures:
            if not settings.twilio_auth_token:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Twilio auth token is not configured",
                )
            if not twilio_utils.is_valid_signature(request, form_dict, settings.twilio_auth_token):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Twilio signature")

        contact_number = form_dict.get("WaId") or form_dict.get("From") or "unknown"
        incoming = (form_dict.get("Body") or "").strip()
        reply = whatsapp_flow.handle_message(db, contact_number, incoming)
        return Response(content=reply, media_type="application/xml")

    return app


app = create_app()

