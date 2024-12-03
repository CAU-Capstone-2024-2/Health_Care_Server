from fastapi import APIRouter
from fastapi.responses import FileResponse


router = APIRouter(tags=["static"])

@router.get("/favicon.ico")
async def favicon():
    return FileResponse("Resources/favicon.ico")