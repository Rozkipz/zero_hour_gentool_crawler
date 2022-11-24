from fastapi import APIRouter, FastAPI
from . import endpoints

api_router = APIRouter()
api_router.include_router(endpoints.player.router)

app = FastAPI()
app.include_router(api_router)

# TODO: Set fastapi to auto reload when code is changed
