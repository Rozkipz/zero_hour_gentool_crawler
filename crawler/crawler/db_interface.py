import models
import psycopg2
import os

conn = psycopg2.connect(os.getenv("DB_CONN"))


def upsert_player(player: models.player.Player):
    upsert = """INSERT INTO player(id, names, first_seen, last_seen) VALUES(%s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET names = %s, last_seen=%s;"""

    with conn.cursor() as curs:
        curs.execute(upsert, (player.player_id, player.names, player.first_seen, player.last_seen, player.names, player.last_seen))
        conn.commit()
