from fastapi import APIRouter, status

from app.core.api.schemas import ORJSONResponse


router = APIRouter(tags=["core"])


@router.get("/healcheck", status_code=status.HTTP_200_OK)
async def healcheck() -> ORJSONResponse:
    return ORJSONResponse("OK")
