from . import db_interface


class NotFoundException(BaseException):
    pass


def get_all_players() -> list:
    players = db_interface.get_all_players()
    print(players)

    return players


def get_player(player_id):
    data = db_interface.get_one_player(player_id)
    if not data:
        raise NotFoundException

    return data
