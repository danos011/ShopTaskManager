from fastapi import APIRouter

router = APIRouter(prefix="/notification", tags=["Notification"])


@router.get("/")
async def ping() -> dict[str, str]:
    pass
