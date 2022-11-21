import psycopg2
from psycopg2.extras import RealDictCursor as DictCursor
import os

conn = psycopg2.connect(os.getenv("DB_CONN"))


def get_all_players() -> list:
    get_all = """SELECT * FROM player"""

    with conn.cursor(cursor_factory=DictCursor) as curs:
        curs.execute(get_all)
        players = curs.fetchall()

    return [dict(player) for player in players]


def get_one_player(player_id: str) -> dict:
    get_player = """SELECT * FROM player WHERE id=%s;"""

    with conn.cursor(cursor_factory=DictCursor) as curs:
        curs.execute(get_player, (player_id,))
        player = curs.fetchone()

    return dict(player)
