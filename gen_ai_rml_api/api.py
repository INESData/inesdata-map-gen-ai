from fastapi import APIRouter

from gen_ai_rml_api.book.rest import router as book_router
from gen_ai_rml_api.user.rest import router as user_router

api_router = APIRouter()

api_router.include_router(user_router, tags=["user"], prefix="/user")
api_router.include_router(book_router, tags=["book"], prefix="/book")


@api_router.get("/health", include_in_schema=False)
async def health():
    """Health check endpoint."""
    return {"status": "ok"}
