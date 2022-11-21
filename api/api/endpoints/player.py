from fastapi import APIRouter, HTTPException
from .. import api_interface

router = APIRouter()


@router.get("/players/")
async def root():
    data = api_interface.get_all_players()
    return {"data": data}


@router.get("/players/{player_id}")
async def get_player(player_id: str):
    try:
        data = api_interface.get_player(player_id)
        return {"data": data}

    except api_interface.NotFoundException:
        raise HTTPException(status_code=404, detail="Player not found.")
